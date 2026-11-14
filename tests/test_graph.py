"""
Тесты модуля graph.
"""
import pytest
import os
import sys
import json
import tempfile

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', 'src'
        )
    )
)

from graph import (
    build_graph,
    _filter_deps,
    _get_deps_from_json,
)

SIMPLE_GRAPH = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D"],
    "D": [],
}

CYCLE_GRAPH = {
    "A": ["B"],
    "B": ["C"],
    "C": ["A"],
}

FILTER_GRAPH = {
    "A": ["B", "C", "D_test"],
    "B": ["E"],
    "C": [],
    "D_test": [],
    "E": [],
}

EXPECTED_SIMPLE_COUNT = 4
EXPECTED_CYCLE_COUNT = 3
EXPECTED_FILTER_COUNT = 4


def _make_getter(graph_data):
    """Создаёт функцию получения зависимостей."""
    def getter(package):
        return graph_data.get(package, [])
    return getter


def test_build_graph_simple():
    """Проверка построения простого графа."""
    getter = _make_getter(SIMPLE_GRAPH)
    graph = build_graph("A", getter)
    assert len(graph) == EXPECTED_SIMPLE_COUNT
    assert "D" in graph


def test_build_graph_cycle():
    """Проверка обработки циклических зависимостей."""
    getter = _make_getter(CYCLE_GRAPH)
    graph = build_graph("A", getter)
    assert len(graph) == EXPECTED_CYCLE_COUNT
    assert "A" in graph
    assert "B" in graph
    assert "C" in graph


def test_build_graph_with_filter():
    """Проверка фильтрации зависимостей."""
    getter = _make_getter(FILTER_GRAPH)
    graph = build_graph("A", getter, filter_str="test")
    assert len(graph) == EXPECTED_FILTER_COUNT
    assert "D_test" not in graph


def test_filter_deps_empty():
    """Проверка фильтра с пустой строкой."""
    deps = ["A", "B", "C"]
    result = _filter_deps(deps, "")
    assert result == deps


def test_filter_deps_with_value():
    """Проверка фильтра с подстрокой."""
    deps = ["alpha", "beta_test", "gamma"]
    result = _filter_deps(deps, "test")
    assert result == ["alpha", "gamma"]


def test_get_deps_from_json():
    """Проверка чтения зависимостей из JSON."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False,
        encoding="utf-8"
    ) as f:
        json.dump(SIMPLE_GRAPH, f)
        tmp_path = f.name
    try:
        deps = _get_deps_from_json(tmp_path, "A")
        assert deps == ["B", "C"]
    finally:
        os.unlink(tmp_path)


def test_get_deps_from_json_missing():
    """Проверка ошибки при отсутствии файла."""
    with pytest.raises(ValueError):
        _get_deps_from_json(
            "/nonexistent.json", "A"
        )


def test_build_graph_single_node():
    """Проверка графа из одного узла."""
    getter = _make_getter({"X": []})
    graph = build_graph("X", getter)
    assert len(graph) == 1
    assert graph["X"] == []
