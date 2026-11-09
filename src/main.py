"""Точка входа инструмента визуализации зависимостей."""

import argparse
import sys
from pathlib import Path

from config import load_config
from nuget import get_direct_dependencies, print_dependencies

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

def main():
    """Загрузить настройки и вывести прямые зависимости."""
    arguments = get_arguments()

    try:
        config = load_config(arguments.config)

        if config["test_mode"]:
            raise ValueError(
                "Тестовый репозиторий будет поддержан на этапе 3."
            )

        version, dependencies = get_direct_dependencies(
            config["repository"],
            config["package_name"],
        )
        print_dependencies(
            config["package_name"],
            version,
            dependencies,
        )
    except ValueError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
