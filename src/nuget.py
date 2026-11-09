"""Получение прямых зависимостей пакетов NuGet."""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen


REQUEST_TIMEOUT = 30
HTTP_NOT_FOUND = 404
VERSION_PARTS_COUNT = 4


def fetch_json(url):
    """Получить JSON по указанному URL."""
    try:
        with urlopen(url, timeout=REQUEST_TIMEOUT) as response:
            return json.load(response)
    except HTTPError as error:
        if error.code == HTTP_NOT_FOUND:
            raise ValueError(
                f"Пакет или ресурс не найден: {url}"
            ) from error

        raise ValueError(
            f"Ошибка HTTP: {error.code}"
        ) from error
    except (URLError, OSError) as error:
        raise ValueError(
            f"Ошибка подключения к репозиторию: {error}"
        ) from error
    except (ValueError, UnicodeError) as error:
        raise ValueError(
            "Репозиторий вернул некорректный JSON."
        ) from error


def get_registration_url(repository):
    """Найти адрес сервиса метаданных в индексе NuGet."""
    index = fetch_json(repository)

    for resource in index["resources"]:
        resource_type = resource.get("@type", "")

        if resource_type.startswith("RegistrationsBaseUrl"):
            return resource["@id"]

    raise ValueError(
        "В репозитории отсутствует сервис метаданных NuGet."
    )


def get_catalog_entries(registration_url, package_name):
    """Получить метаданные всех версий указанного пакета."""
    package_id = quote(package_name.lower(), safe="")
    url = f"{registration_url.rstrip('/')}/{package_id}/index.json"
    index = fetch_json(url)
    entries = []

    for page in index["items"]:
        if "items" not in page:
            page = fetch_json(page["@id"])

        for item in page["items"]:
            entry = item["catalogEntry"]

            if isinstance(entry, str):
                entry = fetch_json(entry)

            entries.append(entry)

    return entries


def version_key(entry):
    """Преобразовать стабильную версию в числовой ключ."""
    version = entry["version"].split("+", maxsplit=1)[0]
    parts = [int(part) for part in version.split(".")]

    while len(parts) < VERSION_PARTS_COUNT:
        parts.append(0)

    return tuple(parts)


def select_latest_version(entries):
    """Выбрать последнюю опубликованную стабильную версию."""
    stable_entries = []

    for entry in entries:
        version = entry["version"].split("+", maxsplit=1)[0]

        if "-" not in version and entry.get("listed", True):
            stable_entries.append(entry)

    if not stable_entries:
        raise ValueError(
            "У пакета отсутствуют опубликованные стабильные версии."
        )

    return max(stable_entries, key=version_key)


def extract_dependencies(entry):
    """Извлечь прямые зависимости по группам платформ."""
    dependencies = []

    for group in entry.get("dependencyGroups", []):
        framework = group.get("targetFramework", "any")

        for dependency in group.get("dependencies", []):
            dependencies.append({
                "name": dependency["id"],
                "range": dependency.get("range", "*"),
                "framework": framework,
            })

    return dependencies


def get_direct_dependencies(repository, package_name):
    """Получить версию пакета и его прямые зависимости."""
    try:
        registration_url = get_registration_url(repository)
        entries = get_catalog_entries(registration_url, package_name)
        latest = select_latest_version(entries)
        dependencies = extract_dependencies(latest)

        return latest["version"], dependencies
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError(
            "Некорректная структура ответа NuGet."
        ) from error


def print_dependencies(package_name, version, dependencies):
    """Вывести прямые зависимости пакета."""
    print(f"Пакет: {package_name}")
    print(f"Версия: {version}")

    if not dependencies:
        print("Прямые зависимости отсутствуют.")
        return

    print("Прямые зависимости:")

    for dependency in dependencies:
        name = dependency["name"]
        version_range = dependency["range"]
        framework = dependency["framework"]
        print(f"  {name} {version_range} [{framework}]")
