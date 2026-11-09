"""Точка входа инструмента визуализации зависимостей."""

import argparse
import sys
from pathlib import Path

from config import load_config
from graph import build_graph, print_graph
from repository import prepare_repository


def get_arguments():
    """Прочитать аргументы командной строки."""
    default_config = (
        Path(__file__).resolve().parent.parent / "config.toml"
    )
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации зависимостей NuGet."
    )
    parser.add_argument(
        "--config",
        default=str(default_config),
        help="Путь к конфигурационному файлу TOML.",
    )

    return parser.parse_args()


def run_application(arguments):
    """Загрузить репозиторий, построить и вывести граф."""
    config = load_config(arguments.config)
    root, loader, _ = prepare_repository(config, arguments.config)
    graph, cycles = build_graph(root, loader)
    print_graph(graph, cycles)


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
