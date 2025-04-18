import itertools
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from glucose import (
    glucose
)


# ----------------------------------
# 1. Функция перехода
# ----------------------------------
def transition(state: tuple[int, int, int], G: float) -> tuple[int, int, int]:
    prev_alpha, prev_beta, prev_delta = state
    new_alpha, new_beta, new_delta = prev_alpha, prev_beta, 0
    if state == (1, 0, 0):
        return (1, 1, 1)
    if state == (0, 1, 0) or state == (0, 1, 1):
        return (1, 1, 1)
    if G >= glucose.G_max_bound:
        new_alpha, new_beta = 0, 1
        return (new_alpha, new_beta, new_delta)
    elif G <= glucose.G_min_bound:
        new_alpha, new_beta = 1, 0
        return (new_alpha, new_beta, new_delta)
    # Дельта-клетки: активируются только если в предыдущем состоянии
    # были активны и альфа, и бета (конфликт)
    if prev_alpha == 1 and prev_beta == 1:
        new_delta = 1
        new_alpha, new_beta = 0, 0  # Сбрасываем конфликт
        return (new_alpha, new_beta, new_delta)
        
    # Задержка деактивации: клетки остаются активными 1 шаг после выхода из их зоны
    if new_alpha == 0 and G > glucose.G_min_bound and G < glucose.G_max_bound:
        new_alpha = prev_alpha  # Сохраняем предыдущее состояние альфа
        return (new_alpha, new_beta, new_delta)
    if new_beta == 0 and G > glucose.G_min_bound and G < glucose.G_max_bound:
        new_beta = prev_beta  # Сохраняем предыдущее состояние бета
        return (new_alpha, new_beta, new_delta)

    return (new_alpha, new_beta, new_delta)
# ----------------------------------
# 2. Словарь имен состояний
# ----------------------------------
state_names = {
    (0, 0, 0): "0, 0, 0",
    (1, 0, 0): "1, 0, 0",
    (0, 1, 0): "0, 1, 0",
    (0, 0, 1): "0, 0, 1",
    (1, 1, 0): "1, 1, 0",
    (1, 0, 1): "1, 0, 1",
    (0, 1, 1): "0, 1, 1",
    (1, 1, 1): "1, 1, 1"
}


# Функция для обратного отображения: по состоянию (кортежу) возвращает строку
def state_label(state):
    return state_names.get(state, str(state))

# ----------------------------------
# 3. Построение ПОЛНОГО графа переходов (по всем (A,B,D) и G ∈ {0,1,2})
# ----------------------------------
def build_full_graph():
    all_states = list(itertools.product([0,1],[0,1],[0,1]))  # 8 состояний
    G_graph = nx.DiGraph()
    # Добавляем узлы
    for s in all_states:
        G_graph.add_node(s)
    edge_labels = {}
    for s in all_states:
        for g in (glucose.G_min, glucose.G_middle, glucose.G_max):
            ns = transition(s, g)
            label_str = f"({g}, {s[0]}, {s[1]}, {s[2]})"
            if (s, ns) not in G_graph.edges():
                G_graph.add_edge(s, ns)
                edge_labels[(s, ns)] = label_str
            else:
                edge_labels[(s, ns)] += "\n" + label_str
    return G_graph, edge_labels


def simulate():
    time_points = np.linspace(0, 100, 100) 
    states_over_time = []
    glucose_over_time = []

    current_state = (1, 0, 0)  # Начальное состояние
    for t in time_points:
        G = glucose.glucose_func(t=t)
        states_over_time.append(current_state)
        glucose_over_time.append(G)
        next_state = transition(current_state, glucose.modify_G(G=G))
        current_state = next_state

    return time_points, states_over_time, glucose_over_time

# ----------------------------------
# 6. Построение графиков: комбинированный граф (глюкоза и состояния)
# ----------------------------------
def plot_simulation1(time_points, states_over_time, glucose_over_time):
    unique = sorted({s for s in states_over_time}, key=lambda s: state_label(s))
    mapping = {s: i for i, s in enumerate(unique)}
    numeric_states = [mapping[s] for s in states_over_time]

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Левая ось Y - состояния автомата
    ax1.step(time_points, numeric_states, where='post', color='red', label='Состояние автомата', linewidth=2)
    ax1.set_xlabel("Время")
    ax1.set_ylabel("Состояние")
    ax1.set_yticks(list(mapping.values()))
    ax1.set_yticklabels([state_label(s) for s in unique])
    ax1.grid(True)

    # Правая ось Y - уровень глюкозы
    ax2 = ax1.twinx()
    ax2.step(time_points, glucose_over_time, where='post', color='black', label='Уровень глюкозы', linewidth=2)
    ax2.set_ylabel(f"Уровень глюкозы (G_min={glucose.G_min}, G_max={glucose.G_max}, G_middle={glucose.G_middle})")
    ax2.set_yticks([glucose.G_min, glucose.G_middle, glucose.G_max])
    ax2.set_ylim(-2.5, 2.5)

    # Добавляем две синие пунктирные линии в позициях G_min_bound и G_max_bound
    ax2.axhline(glucose.G_min_bound, color='blue', linestyle='--', linewidth=2,
                label=f'G_min_bound = {glucose.G_min_bound}')
    ax2.axhline(glucose.G_max_bound, color='blue', linestyle='--', linewidth=2,
                label=f'G_max_bound = {glucose.G_max_bound}')

    # Объединяем легенды
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    plt.title("Моделирование")
    plt.savefig("graph2.png")


#////////////////////////////////////

def plot_simulation(time_points, states_over_time, glucose_over_time, glucose):
    """
    Построение единой фигуры, где:
      - первая ось (subplots[0]) – график уровня глюкозы с нанесёнными горизонтальными
        пунктирными линиями в позициях glucose.G_min_bound и glucose.G_max_bound,
      - следующие оси – графики активности чистых состояний:
            (1, 0, 0), (0, 1, 0) и (0, 0, 1).
    
    Если в каком-то такте значение состояния смешанное, например, (1, 1, 0),
    то считается, что активны и (1, 0, 0), и (0, 1, 0).
    
    Параметры:
      time_points      - массив временных точек
      states_over_time - последовательность состояний автомата, где состояние представлено кортежем,
                         например, (1, 0, 0) или (1, 1, 0)
      glucose_over_time- значения уровня глюкозы по времени
      glucose          - объект с атрибутами:
                         G_min, G_max, G_middle, G_min_bound, G_max_bound
    """
    # Всегда будем выводить 1 график для глюкозы + 3 графика для активности каждой чистой компоненты.
    total_plots = 4
    fig, axes = plt.subplots(total_plots, 1, figsize=(12, 3 * total_plots), sharex=True)
    
    # 1. График уровня глюкозы
    ax0 = axes[0]
    ax0.step(time_points, glucose_over_time, where='post', color='black',
             label='Уровень глюкозы', linewidth=2)
    ax0.set_ylabel("Глюкоза")
    ax0.set_title("Уровень глюкозы")
    ax0.set_ylim(-2.5, 2.5)
    ax0.axhline(glucose.G_min_bound, color='blue', linestyle='--', linewidth=2,
                label=f'G_min_bound = {glucose.G_min_bound}')
    ax0.axhline(glucose.G_max_bound, color='blue', linestyle='--', linewidth=2,
                label=f'G_max_bound = {glucose.G_max_bound}')
    ax0.legend(loc='upper right')
    ax0.grid(True)
    
    state1_activity = [1 if s[0] == 1 else 0 for s in states_over_time]
    state2_activity = [1 if s[1] == 1 else 0 for s in states_over_time]
    state3_activity = [1 if s[2] == 1 else 0 for s in states_over_time]
    
    axes[1].step(time_points, state1_activity, where='post', color='green', linewidth=2)
    axes[1].set_ylabel("(1, 0, 0)")
    axes[1].set_ylim(-0.1, 1.1)
    axes[1].grid(True)
    
    axes[2].step(time_points, state2_activity, where='post', color='orange', linewidth=2)
    axes[2].set_ylabel("(0, 1, 0)")
    axes[2].set_ylim(-0.1, 1.1)
    axes[2].grid(True)
    
    # График для чистого состояния (0, 0, 1)
    axes[3].step(time_points, state3_activity, where='post', color='purple', linewidth=2)
    axes[3].set_ylabel("(0, 0, 1)")
    axes[3].set_ylim(-0.1, 1.1)
    axes[3].grid(True)
    
    # Общая настройка нижней оси
    axes[-1].set_xlabel("Время")
    fig.suptitle("Моделирование: уровень глюкозы и активность чистых состояний", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig("simulation_plot.png")
    plt.show()

if __name__ == "__main__":
    # Строим полный граф переходов
    full_graph, full_edge_labels = build_full_graph()
    pos = nx.spring_layout(full_graph, seed=42)
    plt.figure(figsize=(12, 8))
    nx.draw(full_graph, pos, with_labels=True, labels={s: state_label(s) for s in full_graph.nodes()},
            node_color="lightblue", node_size=1600, font_size=9, arrows=True)
    nx.draw_networkx_edge_labels(full_graph, pos, edge_labels=full_edge_labels, font_color="red", font_size=7)
    plt.title("Полный граф переходов (G∈{0,1,2}, состояния как буквы)")
    plt.savefig("graph.png")

    t_points, states_over_time, glucose_over_time = simulate()
    plot_simulation(t_points, states_over_time, glucose_over_time, glucose)

    # Вывод таблицы переходов
    print("Таблица переходов (24 часа):")
    i = 0
    for t, s, g in zip(t_points, states_over_time, glucose_over_time):
        i+=1
        if i == 1000:
            break
        # print(f"t={t}, G={g}, state={state_label(s)} -> next={state_label(transition(s, g))}")
        print(f"t={t:6.2f}, G={g}, state={state_label(s):10} -> next={state_label(transition(s, g))}")









# 1. Екатерина проверит со мной автомат
# 2. Реализовать более просто автомат: в нем будет 3 состояния (альфа кран, бета кран, l1 * альфа кран и l1 * бета кран).
# 3. Причина резализации 2: сверхвысокочастотные колебания ("шаг интегрирования"). 
# 4. ПОКА БЕЗ ЗАРЕЖКИ.



# (1, 0, 0), (0, 1, 0), (0, 0, 1)


