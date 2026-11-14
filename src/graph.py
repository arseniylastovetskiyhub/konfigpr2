"""
Модуль для построения и анализа графа зависимостей.
Вариант 18, Этап 3.
"""
from collections import deque
import json
import os


def _get_deps_from_json(file_path, package):
    """
    Читает зависимости пакета из JSON-файла.
    :param file_path: Путь к JSON-файлу.
    :param package: Имя пакета.
    :return: Список имён зависимостей.
    """
    if not os.path.isfile(file_path):
        raise ValueError(
            f"Файл графа не найден: {file_path}"
        )
    with open(
        file_path, "r", encoding="utf-8"
    ) as f:
        graph_data = json.load(f)
    return graph_data.get(package, [])


def _filter_deps(deps, filter_str):
    """
    Фильтрует зависимости по подстроке.
    :param deps: Список зависимостей.
    :param filter_str: Подстрока для фильтрации.
    :return: Отфильтрованный список.
    """
    if not filter_str:
        return deps
    return [d for d in deps if filter_str not in d]


def build_graph(start, get_deps_func, filter_str=""):
    """
    Строит граф зависимостей алгоритмом BFS без рекурсии.
    :param start: Начальный пакет.
    :param get_deps_func: Функция получения зависимостей.
    :param filter_str: Подстрока для фильтрации.
    :return: Словарь {пакет: [зависимости]}.
    """
    graph = {}
    visited = set()
    queue = deque([start])
    
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        
        deps = get_deps_func(current)
        deps = _filter_deps(deps, filter_str)
        graph[current] = deps
        
        for dep in deps:
            if dep not in visited:
                queue.append(dep)
    
    return graph


def print_graph_list(graph):
    """
    Выводит граф в виде списка зависимостей.
    :param graph: Словарь графа.
    """
    print("\nГраф зависимостей:")
    for pkg, deps in graph.items():
        if deps:
            deps_str = ", ".join(deps)
            print(f"  {pkg} -> {deps_str}")
        else:
            print(f"  {pkg} -> (нет зависимостей)")


def _build_tree_lines(graph, node, visited, prefix, is_last):
    """
    Строит строки ASCII-дерева для одного узла.
    :param graph: Словарь графа.
    :param node: Текущий узел.
    :param visited: Множество посещённых узлов.
    :param prefix: Префикс строки.
    :param is_last: Является ли узел последним.
    :return: Список строк.
    """
    lines = []
    connector = "└── " if is_last else "├── "
    lines.append(f"{prefix}{connector}{node}")
    
    if node in visited:
        lines[-1] += " (цикл)"
        return lines
    visited.add(node)
    
    deps = graph.get(node, [])
    extension = "    " if is_last else "│   "
    
    for i, dep in enumerate(deps):
        dep_is_last = (i == len(deps) - 1)
        sub_lines = _build_tree_lines(
            graph, dep, visited,
            prefix + extension, dep_is_last
        )
        lines.extend(sub_lines)
    
    return lines


def print_graph_ascii(graph, start):
    """
    Выводит граф в виде ASCII-дерева.
    :param graph: Словарь графа.
    :param start: Корневой пакет.
    """
    print(f"\nASCII-дерево зависимостей ({start}):")
    visited = set()
    lines = _build_tree_lines(
        graph, start, visited, "", True
    )
    for line in lines:
        print(f"  {line}")
