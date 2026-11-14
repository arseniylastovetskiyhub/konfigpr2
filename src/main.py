import argparse
import sys
import os
from urllib.parse import urlparse
from graph import build_graph, print_graph_list, print_graph_ascii

def _check_package(args, errors):
    """Проверяет корректность имени пакета."""
    if not args.package or not args.package.strip():
        errors.append(
            "Ошибка: имя анализируемого "
            "пакета не может быть пустым."
        )


def _check_repo_url(args, errors):
    """Проверяет URL репозитория в обычном режиме."""
    parsed = urlparse(args.repo)
    if not all([parsed.scheme, parsed.netloc]):
        errors.append(
            f"'{args.repo}' не является "
            "корректным URL."
        )


def _check_repo_file(args, errors):
    """Проверяет путь к файлу в тестовом режиме."""
    if not os.path.isfile(args.repo):
        errors.append(
            f"В тестовом режиме путь "
            f"'{args.repo}' должен указывать "
            "на существующий файл."
        )


def _check_repo(args, errors):
    """Проверяет корректность пути к репозиторию."""
    if not args.repo or not args.repo.strip():
        errors.append(
            "Ошибка: URL или путь к "
            "репозиторию не может быть пустым."
        )
        return
    if args.test_mode:
        _check_repo_file(args, errors)
    else:
        _check_repo_url(args, errors)


def _check_output_file(args, errors):
    """Проверяет корректность имени файла с графом."""
    if not args.output_file or not args.output_file.strip():
        errors.append(
            "Ошибка: имя файла с графом "
            "не может быть пустым."
        )


def validate_args(args, errors):
    """Проверяет корректность всех аргументов."""
    _check_package(args, errors)
    _check_repo(args, errors)
    _check_output_file(args, errors)


def build_parser():
    """Создаёт парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализация графа "
                    "зависимостей Maven "
    )
    parser.add_argument(
        "--package",
        default=None,
        help="Имя пакета в формате "
             "'groupId:artifactId[:version]'")
    parser.add_argument(
        "--repo",
        default=None,
        help="URL репозитория или путь к "
             "POM-файлу")
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Режим работы с тестовым "
             "репозиторием")
    parser.add_argument(
        "--output-file",
        default="dependency_graph.png",
        help="Имя файла с изображением графа")
    parser.add_argument(
        "--ascii-tree",
        action="store_true",
        help="Вывод зависимостей в виде "
             "ASCII-дерева")
    parser.add_argument(
        "--filter",
        default="",
        help="Подстрока для фильтрации пакетов")
    return parser


def print_config(args):
    """Выводит параметры в формате ключ-значение."""
    print("Конфигурация приложения:")
    print(f"package: {args.package}")
    print(f"repo: {args.repo}")
    print(f"test_mode: {args.test_mode}")
    print(f"output_file: {args.output_file}")
    print(f"ascii_tree: {args.ascii_tree}")
    print(f"filter: {args.filter}")


def print_dependencies(deps, version, filter_str):
    """
    Выводит список зависимостей на экран.
    :param deps: Список зависимостей.
    :param version: Версия анализируемого пакета.
    :param filter_str: Подстрока для фильтрации.
    """
    print(f"\nПрямые зависимости пакета "
          f"(версия {version}):")
    filtered = deps
    if filter_str:
        filtered = [
            d for d in deps
            if filter_str in d.get("artifactId", "")
        ]
    if not filtered:
        print("  (зависимости не найдены)")
        return
    for dep in filtered:
        group = dep.get("groupId", "?")
        artifact = dep.get("artifactId", "?")
        ver = dep.get("version", "?")
        scope = dep.get("scope", "compile")
        print(f"  - {group}:{artifact}:{ver} "
              f"[{scope}]")


def _make_maven_getter(repo):
    """
    Создаёт функцию получения зависимостей для Maven.
    :param repo: URL репозитория.
    :return: Функция(package) -> [имена].
    """
    from maven import get_dep_names_from_maven
    
    def getter(package):
        return get_dep_names_from_maven(
            repo, package
        )
    
    return getter


def _make_file_getter(file_path):
    """
    Создаёт функцию получения зависимостей из файла.
    :param file_path: Путь к JSON-файлу.
    :return: Функция(package) -> [имена].
    """
    from maven import get_dep_names_from_file
    
    def getter(package):
        return get_dep_names_from_file(
            file_path, package
        )
    
    return getter


def main():
    """
    Точка входа в приложение.
    Парсит аргументы, валидирует, строит граф
    и выводит зависимости.
    """
    parser = build_parser()
    args = parser.parse_args()
    errors = []
    validate_args(args, errors)
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        sys.exit(1)
    print_config(args)
    
    if args.test_mode:
        getter = _make_file_getter(args.repo)
    else:
        getter = _make_maven_getter(args.repo)
    
    try:
        graph = build_graph(
            args.package,
            getter,
            args.filter
        )
        if args.ascii_tree:
            print_graph_ascii(graph, args.package)
        else:
            print_graph_list(graph)
    except ValueError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"\nВсего пакетов в графе: {len(graph)}")
    print("Этап 3 успешно завершён.")


if __name__ == "__main__":
    main()
