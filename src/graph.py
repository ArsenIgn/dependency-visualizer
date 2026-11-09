"""Построение и вывод графа зависимостей."""


VISITING = "visiting"
FINISHED = "finished"


def build_graph(root, get_dependencies):
    """Построить граф итеративным DFS и найти обратные рёбра."""
    graph = {root: list(dict.fromkeys(get_dependencies(root)))}
    states = {root: VISITING}
    cycles = []
    stack = [(root, iter(graph[root]))]

    while stack:
        node, children = stack[-1]
        child = next(children, None)

        if child is None:
            states[node] = FINISHED
            stack.pop()
            continue

        if states.get(child) == VISITING:
            cycles.append((node, child))
            continue

        if child in states:
            continue

        graph[child] = list(dict.fromkeys(get_dependencies(child)))
        states[child] = VISITING
        stack.append((child, iter(graph[child])))

    return graph, cycles


def print_graph(graph, cycles):
    """Вывести списки смежности и обнаруженные циклы."""
    print("Граф зависимостей:")

    for node, dependencies in graph.items():
        children = ", ".join(dependencies) or "нет зависимостей"
        print(f"{node}: {children}")

    if cycles:
        print("Обратные рёбра, замыкающие циклы:")

        for source, target in cycles:
            print(f"  {source} -> {target}")
