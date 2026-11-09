"""Вывод ASCII-дерева и построение диаграммы PlantUML."""

import subprocess
import webbrowser
from pathlib import Path


RENDER_TIMEOUT = 120


def print_ascii_tree(graph, root):
    """Вывести дерево без рекурсии, отмечая повторные вершины."""
    print(root)
    visited = {root}
    stack = []

    def push_children(node, prefix):
        """Добавить дочерние вершины в стек."""
        children = graph[node]
        last_index = len(children) - 1

        for index in reversed(range(len(children))):
            stack.append((
                children[index],
                prefix,
                index == last_index,
            ))

    push_children(root, "")

    while stack:
        node, prefix, is_last = stack.pop()
        connector = "`-- " if is_last else "|-- "

        if node in visited:
            print(f"{prefix}{connector}{node} [повтор или цикл]")
            continue

        print(f"{prefix}{connector}{node}")
        visited.add(node)
        child_prefix = prefix + ("    " if is_last else "|   ")
        push_children(node, child_prefix)


def create_plantuml(graph):
    """Сформировать текст диаграммы зависимостей."""
    aliases = {
        node: f"node_{index}"
        for index, node in enumerate(graph)
    }
    lines = [
        "@startuml",
        "left to right direction",
        "skinparam shadowing false",
    ]

    for node, alias in aliases.items():
        label = node.replace("\\", "\\\\").replace('"', '\\"')
        label = label.replace("\r", " ").replace("\n", " ")
        lines.append(f'rectangle "{label}" as {alias}')

    for source, dependencies in graph.items():
        for target in dependencies:
            lines.append(f"{aliases[source]} --> {aliases[target]}")

    lines.append("@enduml")

    return "\n".join(lines) + "\n"


def render_image(source_path, jar_path):
    """Сформировать PNG с помощью локального PlantUML."""
    jar_path = Path(jar_path).resolve()

    if not jar_path.is_file():
        raise ValueError(f"Файл PlantUML не найден: {jar_path}")

    image_path = source_path.with_suffix(".svg")
    image_path.unlink(missing_ok=True)
    command = [
        "java",
        "-jar",
        str(jar_path),
        "-charset",
        "UTF-8",
        "-tsvg",
        str(source_path),
    ]

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=RENDER_TIMEOUT,
        )
    except subprocess.CalledProcessError as error:
        raise ValueError(
            f"Ошибка PlantUML: {error.stderr or error.stdout}"
        ) from error
    except subprocess.TimeoutExpired as error:
        raise ValueError("Превышено время отрисовки.") from error

    if not image_path.is_file():
        raise ValueError("PlantUML не создал изображение.")
    return image_path


def visualize_graph(graph, jar_path):
    """Сохранить PlantUML, создать и открыть изображение."""
    project_directory = Path(__file__).resolve().parent.parent
    output_directory = project_directory / "output"
    output_directory.mkdir(parents=True, exist_ok=True)
    source_path = output_directory / "graph.puml"
    source_path.write_text(create_plantuml(graph), encoding="utf-8")
    print(f"Диаграмма PlantUML: {source_path}")
    image_path = render_image(source_path, jar_path)
    print(f"Изображение: {image_path}")

    if not webbrowser.open(image_path.as_uri()):
        print("Откройте изображение вручную по указанному пути.")
