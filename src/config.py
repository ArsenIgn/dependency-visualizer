"""Чтение и проверка конфигурации приложения."""

import tomllib
from pathlib import Path
from urllib.parse import urlsplit


def validate_text(config, key):
    """Проверить, что параметр является непустой строкой."""
    value = config.get(key)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"Параметр '{key}' должен быть непустой строкой."
        )

    return value.strip()


def validate_bool(config, key):
    """Проверить, что параметр имеет логический тип."""
    value = config.get(key)

    if not isinstance(value, bool):
        raise ValueError(
            f"Параметр '{key}' должен быть true или false."
        )

    return value


def validate_repository(repository, test_mode, config_directory):
    """Проверить URL репозитория или путь к тестовому файлу."""
    if test_mode:
        repository_path = Path(repository)

        if not repository_path.is_absolute():
            repository_path = config_directory / repository_path

        if not repository_path.is_file():
            raise ValueError(
                f"Файл тестового репозитория не найден: {repository}"
            )

        return

    try:
        address = urlsplit(repository)
        address.port
    except ValueError as error:
        raise ValueError("Некорректный URL репозитория.") from error

    if (
        address.scheme not in ("http", "https")
        or not address.hostname
        or any(character.isspace() for character in repository)
    ):
        raise ValueError(
            "Репозиторий должен иметь корректный HTTP или HTTPS URL."
        )


def load_config(config_path):
    """Загрузить TOML и проверить обязательные параметры."""
    path = Path(config_path)

    try:
        with path.open("rb") as file:
            config = tomllib.load(file)
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"Ошибка синтаксиса TOML: {error}") from error
    except OSError as error:
        raise ValueError(
            f"Не удалось прочитать конфигурацию: {error}"
        ) from error

    package_name = validate_text(config, "package_name")
    repository = validate_text(config, "repository")
    test_mode = validate_bool(config, "test_mode")
    ascii_tree = validate_bool(config, "ascii_tree")

    validate_repository(repository, test_mode, path.resolve().parent)

    return {
        "package_name": package_name,
        "repository": repository,
        "test_mode": test_mode,
        "ascii_tree": ascii_tree,
    }
