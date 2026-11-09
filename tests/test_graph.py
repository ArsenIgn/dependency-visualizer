"""Проверки итеративного обхода графа."""

import unittest

from src.graph import build_graph


class GraphTests(unittest.TestCase):
    """Проверки цепочек, ветвлений и циклов."""

    def test_chain(self):
        """Обход должен включать транзитивные зависимости."""
        repository = {
            "A": ["B"],
            "B": ["C"],
            "C": [],
        }

        graph, cycles = build_graph("A", repository.__getitem__)

        self.assertEqual(graph, repository)
        self.assertEqual(cycles, [])

    def test_shared_dependency(self):
        """Общую зависимость нужно загружать один раз."""
        repository = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }
        calls = []

        def loader(name):
            """Записать обращение и вернуть зависимости."""
            calls.append(name)
            return repository[name]

        graph, cycles = build_graph("A", loader)

        self.assertEqual(graph, repository)
        self.assertEqual(calls.count("D"), 1)
        self.assertEqual(cycles, [])

    def test_cycle(self):
        """Цикл не должен приводить к бесконечному обходу."""
        repository = {
            "A": ["B"],
            "B": ["A"],
        }

        graph, cycles = build_graph("A", repository.__getitem__)

        self.assertEqual(graph, repository)
        self.assertEqual(cycles, [("B", "A")])

    def test_self_reference(self):
        """Обход должен распознавать самоссылку."""
        graph, cycles = build_graph("A", lambda name: ["A"])

        self.assertEqual(graph, {"A": ["A"]})
        self.assertEqual(cycles, [("A", "A")])

    def test_isolated_node(self):
        """Вершина без зависимостей должна сохраняться."""
        graph, cycles = build_graph("A", lambda name: [])

        self.assertEqual(graph, {"A": []})
        self.assertEqual(cycles, [])


if __name__ == "__main__":
    unittest.main()
