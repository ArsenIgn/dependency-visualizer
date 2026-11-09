"""Точка входа инструмента визуализации зависимостей."""

import argparse
import sys
from pathlib import Path

from config import load_config
from graph import build_graph, print_graph
from repository import prepare_repository
from reverse import print_reverse_dependencies
from visualization import print_ascii_tree, visualize_graph


def get_arguments():
    """Прочитать аргументы командной строки."""
    project_directory = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации зависимостей NuGet."
    )
    parser.add_argument(
        "--config",
        default=str(project_directory / "config.toml"),
        help="Путь к конфигурационному файлу TOML.",
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="Вывести обратные зависимости тестового пакета.",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Создать и открыть изображение графа.",
    )
    parser.add_argument(
        "--plantuml-jar",
        default=str(project_directory / "tools" / "plantuml.jar"),
        help="Путь к файлу PlantUML JAR.",
    )

    return parser.parse_args()


def run_application(arguments):
    """Построить граф или найти обратные зависимости."""
    config = load_config(arguments.config)
    root, loader, repository = prepare_repository(
        config,
        arguments.config,
    )

    if arguments.reverse:
        if repository is None:
            raise ValueError(
                "Обратный поиск доступен для тестового репозитория."
            )

        print_reverse_dependencies(repository, root)
        return

    graph, cycles = build_graph(root, loader)
    print_graph(graph, cycles)
    if config["ascii_tree"]:
        print("ASCII-дерево зависимостей:")
        print_ascii_tree(graph, root)

    if arguments.visualize:
        visualize_graph(graph, arguments.plantuml_jar)


def main():
    """Запустить приложение с обработкой ошибок."""
    arguments = get_arguments()

    try:
        run_application(arguments)
    except (ValueError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
