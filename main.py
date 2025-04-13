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

    if G >= glucose.G_max_bound:
        new_alpha, new_beta = 0, 1
    elif G <= glucose.G_min_bound:
        new_alpha, new_beta = 1, 0

    # Дельта-клетки: активируются только если в предыдущем состоянии
    # были активны и альфа, и бета (конфликт)
    if prev_alpha == 1 and prev_beta == 1:
        new_delta = 1
        new_alpha, new_beta = 0, 0  # Сбрасываем конфликт
        
    # Задержка деактивации: клетки остаются активными 1 шаг после выхода из их зоны
    if new_alpha == 0 and G > glucose.G_min_bound and G < glucose.G_max_bound:
        new_alpha = prev_alpha  # Сохраняем предыдущее состояние альфа
    if new_beta == 0 and G > glucose.G_min_bound and G < glucose.G_max_bound:
        new_beta = prev_beta  # Сохраняем предыдущее состояние бета

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
    time_points = np.linspace(0, 100, 1000) 
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
def plot_simulation(time_points, states_over_time, glucose_over_time):
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

    # Симулируем 24 часа
    t_points, states_over_time, glucose_over_time = simulate()
    plot_simulation(t_points, states_over_time, glucose_over_time)

    # Вывод таблицы переходов
    print("Таблица переходов (24 часа):")
    i = 0
    for t, s, g in zip(t_points, states_over_time, glucose_over_time):
        i+=1
        if i == 1000:
            break
        # print(f"t={t}, G={g}, state={state_label(s)} -> next={state_label(transition(s, g))}")
        print(f"t={t:6.2f}, G={g}, state={state_label(s):10} -> next={state_label(transition(s, g))}")

