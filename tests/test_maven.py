"""
Тесты модуля maven.
"""
import pytest
import os
import sys
import tempfile

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', 'src'
        )
    )
)

from maven import (
    parse_package_name,
    parse_dependencies,
    group_to_path,
    build_pom_url,
    get_dependencies,
)


SAMPLE_POM = """<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <groupId>com.example</groupId>
  <artifactId>my-app</artifactId>
  <version>1.0</version>
  <dependencies>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.13.2</version>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.springframework</groupId>
      <artifactId>spring-core</artifactId>
      <version>5.3.20</version>
    </dependency>
  </dependencies>
</project>"""

EMPTY_POM = """<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <groupId>com.example</groupId>
  <artifactId>empty-app</artifactId>
  <version>1.0</version>
</project>"""

EXPECTED_DEPS_COUNT = 2
EXPECTED_EMPTY_COUNT = 0

def test_parse_package_name_full():
    """Проверка разбора полного имени пакета."""
    g, a, v = parse_package_name(
        "org.spring:spring-core:5.3.20"
    )
    assert g == "org.spring"
    assert a == "spring-core"
    assert v == "5.3.20"


def test_parse_package_name_no_version():
    """Проверка разбора имени без версии."""
    g, a, v = parse_package_name("org.spring:spring-core")
    assert g == "org.spring"
    assert a == "spring-core"
    assert v is None


def test_parse_package_name_invalid():
    """Проверка ошибки при неверном формате."""
    with pytest.raises(ValueError):
        parse_package_name("invalid")


def test_group_to_path():
    """Проверка преобразования groupId в путь."""
    result = group_to_path("org.springframework")
    assert result == "org/springframework"


def test_build_pom_url():
    """Проверка построения URL к POM."""
    url = build_pom_url(
        "https://repo.maven.org",
        "org.spring", "core", "1.0"
    )
    expected = (
        "https://repo.maven.org/org/spring/core"
        "/1.0/core-1.0.pom"
    )
    assert url == expected


def test_parse_dependencies():
    """Проверка парсинга зависимостей."""
    deps = parse_dependencies(SAMPLE_POM)
    assert len(deps) == EXPECTED_DEPS_COUNT
    assert deps[0]["artifactId"] == "junit"
    assert deps[0]["scope"] == "test"
    assert deps[1]["artifactId"] == "spring-core"


def test_parse_dependencies_empty():
    """Проверка парсинга POM без зависимостей."""
    deps = parse_dependencies(EMPTY_POM)
    assert len(deps) == EXPECTED_EMPTY_COUNT


def test_get_dependencies_from_file():
    """Проверка чтения зависимостей из файла."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".pom", delete=False,
        encoding="utf-8"
    ) as f:
        f.write(SAMPLE_POM)
        tmp_path = f.name
    try:
        deps, version = get_dependencies(
            tmp_path, "any:any", test_mode=True
        )
        assert len(deps) == EXPECTED_DEPS_COUNT
        assert version == "test"
    finally:
        os.unlink(tmp_path)


def test_get_dependencies_file_not_found():
    """Проверка ошибки при отсутствии файла."""
    with pytest.raises(ValueError):
        get_dependencies(
            "/nonexistent.pom",
            "any:any",
            test_mode=True
        )
