"""Поиск обратных зависимостей в тестовом репозитории."""

from graph import build_graph


def reverse_graph(graph):
    """Развернуть направления всех рёбер графа."""
    reversed_graph = {node: [] for node in graph}

    for source, dependencies in graph.items():
        for target in dependencies:
            reversed_graph[target].append(source)

    return reversed_graph


def print_reverse_dependencies(repository, package_name):
    """Найти прямые и транзитивные обратные зависимости."""
    if package_name not in repository:
        raise ValueError(
            f"Пакет {package_name} отсутствует в репозитории."
        )

    reversed_graph = reverse_graph(repository)
    graph, _ = build_graph(
        package_name,
        reversed_graph.__getitem__,
    )
    dependencies = sorted(
        node for node in graph if node != package_name
    )
    print(f"Обратные зависимости пакета {package_name}:")

    if not dependencies:
        print("Отсутствуют.")
        return

    for dependency in dependencies:
        print(f"  {dependency}")
