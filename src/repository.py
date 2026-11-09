"""Работа с тестовым репозиторием и NuGet."""

import json
import re
from pathlib import Path

from nuget import get_direct_dependencies


def validate_test_graph(graph):
    """Проверить имена пакетов и ссылки тестового графа."""
    if not isinstance(graph, dict) or not graph:
        raise ValueError("Тестовый репозиторий должен быть объектом JSON.")

    for name, dependencies in graph.items():
        if not re.fullmatch(r"[A-Z]+", name):
            raise ValueError(
                "Имена тестовых пакетов должны состоять из букв A-Z."
            )

        if not isinstance(dependencies, list):
            raise ValueError(f"Зависимости {name} должны быть списком.")

        for dependency in dependencies:
            if not isinstance(dependency, str):
                raise ValueError("Имя зависимости должно быть строкой.")

            if dependency not in graph:
                raise ValueError(
                    f"Пакет {dependency} отсутствует в репозитории."
                )


def load_test_repository(repository, config_path):
    """Прочитать тестовый граф из JSON-файла."""
    path = Path(repository)

    if not path.is_absolute():
        path = Path(config_path).resolve().parent / path

    try:
        with path.open("r", encoding="utf-8") as file:
            graph = json.load(file)
    except (OSError, ValueError) as error:
        raise ValueError(
            f"Не удалось прочитать тестовый репозиторий: {error}"
        ) from error

    validate_test_graph(graph)

    return graph


def create_test_loader(graph):
    """Создать функцию получения тестовых зависимостей."""
    def get_dependencies(name):
        """Вернуть зависимости существующего тестового пакета."""
        if name not in graph:
            raise ValueError(f"Пакет {name} отсутствует в репозитории.")

        return graph[name]

    return get_dependencies


def create_nuget_loader(repository):
    """Создать загрузчик с кешированием и нормализацией имён."""
    cache = {}

    def get_dependencies(name):
        """Получить зависимости последней стабильной версии."""
        package_id = name.lower()

        if package_id not in cache:
            version, dependencies = get_direct_dependencies(
                repository,
                package_id,
            )
            print(f"Загружен пакет: {package_id} {version}")
            cache[package_id] = sorted({
                dependency["name"].lower()
                for dependency in dependencies
            })

        return cache[package_id]

    return get_dependencies


def prepare_repository(config, config_path):
    """Подготовить корень, загрузчик и тестовый репозиторий."""
    if config["test_mode"]:
        graph = load_test_repository(
            config["repository"],
            config_path,
        )
        loader = create_test_loader(graph)

        return config["package_name"], loader, graph

    root = config["package_name"].lower()
    loader = create_nuget_loader(config["repository"])

    return root, loader, None
