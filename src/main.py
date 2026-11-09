"""Точка входа инструмента визуализации зависимостей."""

import argparse
import sys
from pathlib import Path

from config import load_config


def main():
    """Прочитать конфигурацию и вывести параметры приложения."""
    default_config = Path(__file__).resolve().parent.parent / "config.toml"

    parser = argparse.ArgumentParser(
        description="Инструмент визуализации зависимостей NuGet."
    )
    parser.add_argument(
        "--config",
        default=str(default_config),
        help="Путь к конфигурационному файлу TOML.",
    )
    arguments = parser.parse_args()

    try:
        config = load_config(arguments.config)
    except ValueError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    for key, value in config.items():
        if isinstance(value, bool):
            value = str(value).lower()

        print(f"{key} = {value}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
