"""
Модуль для работы с репозиторием Maven.
Вариант 18, Этап 2.
"""
import os
import urllib.request
import urllib.error
import xml.etree.ElementTree as element_tree


MAVEN_POM_NS = "{http://maven.apache.org/POM/4.0.0}"
MIN_PARTS = 2
MAX_PARTS = 3

def parse_package_name(package):
    """
    Разбирает имя пакета Maven на компоненты.
    :param package: Строка вида 'groupId:artifactId[:version]'.
    :return: Кортеж (group_id, artifact_id, version).
    """
    parts = package.split(":")
    if len(parts) < MIN_PARTS or len(parts) > MAX_PARTS:
        raise ValueError(
            "Неверный формат пакета. "
            "Ожидается 'groupId:artifactId[:version]'."
        )
    group_id = parts[0]
    artifact_id = parts[1]
    version = parts[MAX_PARTS - 1] if len(parts) == MAX_PARTS else None
    return group_id, artifact_id, version


def group_to_path(group_id):
    """
    Преобразует groupId в путь URL.
    :param group_id: Например, 'org.springframework'.
    :return: Путь, например, 'org/springframework'.
    """
    return group_id.replace(".", "/")


def build_pom_url(repo, group_id, artifact_id, version):
    """
    Строит URL к POM-файлу пакета.
    :param repo: Базовый URL репозитория.
    :param group_id: Идентификатор группы.
    :param artifact_id: Идентификатор артефакта.
    :param version: Версия пакета.
    :return: Полный URL к POM-файлу.
    """
    group_path = group_to_path(group_id)
    base = repo.rstrip("/")
    return (
        f"{base}/{group_path}/{artifact_id}"
        f"/{version}/{artifact_id}-{version}.pom"
    )


def build_metadata_url(repo, group_id, artifact_id):
    """
    Строит URL к файлу метаданных Maven.
    :param repo: Базовый URL репозитория.
    :param group_id: Идентификатор группы.
    :param artifact_id: Идентификатор артефакта.
    :return: URL к maven-metadata.xml.
    """
    group_path = group_to_path(group_id)
    base = repo.rstrip("/")
    return (
        f"{base}/{group_path}/{artifact_id}"
        "/maven-metadata.xml"
    )


def fetch_url(url):
    """
    Скачивает содержимое по URL.
    :param url: Адрес для загрузки.
    :return: Строка с содержимым.
    """
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raise ValueError(
            f"Ошибка HTTP {e.code} при запросе {url}"
        ) from e
    except urllib.error.URLError as e:
        raise ValueError(
            f"Ошибка сети при запросе {url}: {e.reason}"
        ) from e


def get_latest_version(repo, group_id, artifact_id):
    """
    Получает последнюю версию из метаданных Maven.
    :param repo: Базовый URL репозитория.
    :param group_id: Идентификатор группы.
    :param artifact_id: Идентификатор артефакта.
    :return: Строка с номером версии.
    """
    url = build_metadata_url(repo, group_id, artifact_id)
    content = fetch_url(url)
    root = element_tree.fromstring(content)
    versioning = root.find("versioning")
    if versioning is None:
        raise ValueError(
            f"Нет секции versioning в {url}"
        )
    
    latest = versioning.find("latest")
    if latest is not None and latest.text:
        return latest.text
    
    release = versioning.find("release")
    if release is not None and release.text:
        return release.text
    
    raise ValueError(
        f"Не удалось найти версию в {url}"
    )


def resolve_version(repo, group_id, artifact_id, version):
    """
    Определяет версию пакета.
    :param repo: Базовый URL репозитория.
    :param group_id: Идентификатор группы.
    :param artifact_id: Идентификатор артефакта.
    :param version: Версия или None.
    :return: Разрешённая версия.
    """
    if version:
        return version
    return get_latest_version(repo, group_id, artifact_id)


def _extract_properties(root):
    """
    Извлекает свойства Maven из POM.
    :param root: Корневой элемент XML.
    :return: Словарь {имя_свойства: значение}.
    """
    props = {}
    ns = MAVEN_POM_NS
    properties = root.find(f"{ns}properties")
    if properties is None:
        return props
    for prop in properties:
        tag = prop.tag
        if tag.startswith(ns):
            tag = tag[len(ns):]
        if prop.text:
            props[tag] = prop.text
    return props


def _resolve_property(value, props):
    """
    Заменяет ${...} на значения из свойств.
    :param value: Строка с возможными ${...}.
    :param props: Словарь свойств Maven.
    :return: Строка с разрешёнными свойствами.
    """
    if not value:
        return value
    import re
    def replacer(match):
        name = match.group(1)
        return props.get(name, match.group(0))
    return re.sub(r"\$\{([^}]+)\}", replacer, value)

def _parse_one_dep(dep, ns, props):
    """
    Парсит одну зависимость из XML.
    :param dep: Элемент dependency.
    :param ns: Namespace Maven.
    :param props: Словарь свойств.
    :return: Словарь или None.
    """
    group = dep.find(f"{ns}groupId")
    artifact = dep.find(f"{ns}artifactId")
    if group is None or artifact is None:
        return None
    info = {
        "groupId": group.text or "",
        "artifactId": artifact.text or "",
    }
    version = dep.find(f"{ns}version")
    if version is not None and version.text:
        info["version"] = _resolve_property(
            version.text, props
        )
    scope = dep.find(f"{ns}scope")
    if scope is not None and scope.text:
        info["scope"] = scope.text
    return info

def parse_dependencies(pom_content):
    """
    Извлекает прямые зависимости из POM-файла.
    :param pom_content: Строка с содержимым POM.
    :return: Список словарей с зависимостями.
    """
    root = element_tree.fromstring(pom_content)
    props = _extract_properties(root)
    deps = []
    ns = MAVEN_POM_NS
    dependencies = root.find(f"{ns}dependencies")
    if dependencies is None:
        return deps
    for dep in dependencies.findall(f"{ns}dependency"):
        parsed = _parse_one_dep(dep, ns, props)
        if parsed is not None:
            deps.append(parsed)
    return deps


def _get_deps_from_file(file_path):
    """
    Читает и парсит локальный POM-файл.
    :param file_path: Путь к POM-файлу.
    :return: Список зависимостей.
    """
    if not os.path.isfile(file_path):
        raise ValueError(f"Файл не найден: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return parse_dependencies(content)


def _get_deps_from_url(repo, package):
    """
    Скачивает и парсит POM по URL.
    :param repo: URL репозитория.
    :param package: Имя пакета.
    :return: Список зависимостей.
    """
    group_id, artifact_id, version = parse_package_name(package)
    resolved = resolve_version(
        repo, group_id, artifact_id, version
    )
    pom_url = build_pom_url(
        repo, group_id, artifact_id, resolved
    )
    pom_content = fetch_url(pom_url)
    return parse_dependencies(pom_content), resolved


def get_dependencies(repo, package, test_mode=False):
    """
    Получает прямые зависимости пакета Maven.
    :param repo: URL репозитория или путь к POM-файлу.
    :param package: Имя пакета в формате Maven.
    :param test_mode: Флаг тестового режима.
    :return: Кортеж (список зависимостей, версия).
    """
    if test_mode:
        deps = _get_deps_from_file(repo)
        return deps, "test"
    deps, version = _get_deps_from_url(repo, package)
    return deps, version
