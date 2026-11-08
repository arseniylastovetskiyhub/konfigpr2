import pytest
import sys
import os

"""Перед импортом модулей возвращаемся в src"""
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', 'src'
        )
    )
)

from main import validate_args
from argparse import Namespace


def _make_errors():
    """Создаёт пустой список ошибок."""
    return []


def test_valid_args():
    """Проверка корректных аргументов."""
    args = Namespace(
        package="requests",
        repo="https://example.com/repo",
        test_mode=False,
        output_file="graph.png",
        ascii_tree=True,
        filter="test"
    )
    errors = _make_errors()
    validate_args(args, errors)
    assert len(errors) == 0


def test_empty_package():
    """Проверка ошибки при пустом пакете."""
    args = Namespace(
        package="",
        repo="https://example.com/repo",
        test_mode=False,
        output_file="graph.png",
        ascii_tree=False,
        filter=""
    )
    errors = _make_errors()
    validate_args(args, errors)
    assert len(errors) >= 1
    assert "пакета" in errors[0]


def test_invalid_url():
    """Проверка ошибки при невалидном URL."""
    args = Namespace(
        package="requests",
        repo="not-a-valid-url",
        test_mode=False,
        output_file="graph.png",
        ascii_tree=False,
        filter=""
    )
    errors = _make_errors()
    validate_args(args, errors)
    assert len(errors) >= 1
    assert "URL" in errors[0]


def test_test_mode_missing_file():
    """Проверка ошибки при отсутствии файла."""
    args = Namespace(
        package="requests",
        repo="C:\\nonexistent\\file.txt",
        test_mode=True,
        output_file="graph.png",
        ascii_tree=False,
        filter=""
    )
    errors = _make_errors()
    validate_args(args, errors)
    assert len(errors) >= 1


def test_empty_output_file():
    """Проверка ошибки при пустом имени файла."""
    args = Namespace(
        package="requests",
        repo="https://example.com/repo",
        test_mode=False,
        output_file="",
        ascii_tree=False,
        filter=""
    )
    errors = _make_errors()
    validate_args(args, errors)
    assert len(errors) >= 1
    assert "файла" in errors[0]


def test_empty_repo():
    """Проверка ошибки при пустом репозитории."""
    args = Namespace(
        package="requests",
        repo="",
        test_mode=False,
        output_file="graph.png",
        ascii_tree=False,
        filter=""
    )
    errors = _make_errors()
    validate_args(args, errors)
    assert len(errors) >= 1
    assert "репозиторию" in errors[0]
