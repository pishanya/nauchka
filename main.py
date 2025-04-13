import itertools
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import math


def modify_G(G: float) -> int:
    if G < 0.8:
        return 0  # LOW
    elif G < 1.5:
        return 1  # NORMAL
    return 2# HIGH


# ----------------------------------
# 1. Функция перехода
# ----------------------------------
def transition(state: tuple[int, int, int], G: float) -> tuple[int, int, int]:
    G: int = modify_G(G=G)
    prev_alpha, prev_beta, prev_delta = state
    new_alpha, new_beta, new_delta = prev_alpha, prev_beta, 0

    # Гистерезис: зона гомеостаза 3.5 <= G <= 5.5
    if G >= 1.2:
        new_alpha, new_beta = 0, 1
    elif G <= 0.8:
        new_alpha, new_beta = 1, 0
    else:
        # Сохраняем предыдущее состояние в зоне гомеостаза
        pass

    # Дельта-клетки: активируются только если в предыдущем состоянии
    # были активны и альфа, и бета (конфликт)
    if prev_alpha == 1 and prev_beta == 1:
        new_delta = 1
        new_alpha, new_beta = 0, 0  # Сбрасываем конфликт
        
    # Задержка деактивации: клетки остаются активными 1 шаг после выхода из их зоны
    if new_alpha == 0 and G > 0.8 and G < 1.2:
        new_alpha = prev_alpha  # Сохраняем предыдущее состояние альфа
    if new_beta == 0 and G > 0.8 and G < 1.2:
        new_beta = prev_beta  # Сохраняем предыдущее состояние бета

    return (new_alpha, new_beta, new_delta)
# ----------------------------------
# 2. Словарь имен состояний
# ----------------------------------
state_names = {
    (0,0,0): "0, 0, 0",
    (1,0,0): "1, 0, 0",
    (0,1,0): "0, 1, 0",
    (0,0,1): "0, 0, 1",
    (1,1,0): "1, 1, 0",
    (1,0,1): "1, 0, 1",
    (0,1,1): "0, 1, 1",
    (1,1,1): "1, 1, 1"
}

# Функция для обратного отображения: по состоянию (кортежу) возвращает строку
def state_label(state):
    return state_names.get(state, str(state))

# ----------------------------------
# 3. Построение ПОЛНОГО графа переходов (по всем (A,B,D) и G ∈ {0,1,2})
# ----------------------------------
def build_full_graph():
    all_states = list(itertools.product([0,1],[0,1],[0,1]))  # 8 состояний
    all_G = [0,1,2]  # G=0,1,2
    G_graph = nx.DiGraph()
    # Добавляем узлы
    for s in all_states:
        G_graph.add_node(s)
    edge_labels = {}
    for s in all_states:
        for g in all_G:
            ns = transition(s, g)
            label_str = f"({g}, {s[0]}, {s[1]}, {s[2]})"
            if (s, ns) not in G_graph.edges():
                G_graph.add_edge(s, ns)
                edge_labels[(s, ns)] = label_str
            else:
                edge_labels[(s, ns)] += "\n" + label_str
    return G_graph, edge_labels


def glucose_pattern(t: float) -> int:
    return 1 + np.sin(t/2)


def bar(t: float, amplitude=2, period=2):
    return amplitude * ((t % period) < (period / 2))


def simulate():
    time_points = np.linspace(0, 100, 1000)  # от 0 до 24 (24 не включается)
    states_over_time = []
    glucose_over_time = []

    current_state = (1, 0, 0)  # Начальное состояние
    for t in time_points:
        G = glucose_pattern(t)
        states_over_time.append(current_state)
        glucose_over_time.append(G)
        next_state = transition(current_state, G)
        current_state = next_state

    return time_points, states_over_time, glucose_over_time

# ----------------------------------
# 6. Построение графиков: комбинированный граф (глюкоза и состояния)
# ----------------------------------
def plot_24h(time_points, states_over_time, glucose_over_time):
    unique = sorted({s for s in states_over_time}, key=lambda s: state_label(s))
    mapping = {s: i for i, s in enumerate(unique)}
    numeric_states = [mapping[s] for s in states_over_time]

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Левая ось Y - состояния автомата
    ax1.step(time_points, numeric_states, where='post', color='red', label='Состояние автомата', linewidth=2)
    ax1.set_xlabel("Время (часы)")
    ax1.set_ylabel("Состояние")
    ax1.set_yticks(list(mapping.values()))
    ax1.set_yticklabels([state_label(s) for s in unique])
    ax1.grid(True)

    # Правая ось Y - уровень глюкозы
    ax2 = ax1.twinx()
    ax2.step(time_points, glucose_over_time, where='post', color='black', label='Уровень глюкозы', linewidth=2)
    ax2.set_ylabel("Уровень глюкозы (0=LOW,1=NORM,2=HIGH)")
    ax2.set_yticks([0, 1, 2])
    ax2.set_ylim(-0.5, 2.5)

    # Объединяем легенды
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    plt.title("Моделирование за 24 часа")
    plt.savefig("graph2.png")

# ----------------------------------
# 7. Основной блок: построение графа, симуляция и вывод графиков и таблицы переходов
# ----------------------------------
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
    plot_24h(t_points, states_over_time, glucose_over_time)

    # Вывод таблицы переходов
    print("Таблица переходов (24 часа):")
    i = 0
    for t, s, g in zip(t_points, states_over_time, glucose_over_time):
        i+=1
        if i == 1000:
            break
        # print(f"t={t}, G={g}, state={state_label(s)} -> next={state_label(transition(s, g))}")
        print(f"t={t:6.2f}, G={g}, state={state_label(s):10} -> next={state_label(transition(s, g))}")

