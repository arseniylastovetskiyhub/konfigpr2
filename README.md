\# CLI-приложение



Инструмент визуализации графа зависимостей.
Вариант 18.



\## Структура проекта



```text
my-shell/
├── src/
│   ├── \_\_init\_\_.py                # Делает папку src модулем Python
│   └── main.py                    # Главный файл
│   └── maven.py                   # Работа с Maven-репозиторием
│   └── graph.py                   # Построение и анализ графа
├── tests/
│   ├── \_\_init\_\_.py                # Делает папку tests модулем Python
│   ├── test\_main.bat  		    # Тест
│   ├── test\_maven.py              # Тесты парсера Maven
│   ├── test\_graph.py              # Тесты графа зависимостей
│   └── sample.pom                 # Тестовый POM-файл
├── run.bat                        # Скрипт запуска для Windows
├── README.md                      # Документация проекта
└── .gitignore                     # Список файлов, игнорируемых Git
```



\## Запуск



Запуск делается через комнадную строку при помощи команды:



```text
run.bat --package "groupId:artifactId\[:version]" --repo "https://repo1.maven.org/maven2"
```



\## Параметры



* `--package` - имя анализируемого пакета (обязательный)
* `--repo` - URL репозитория или путь к файлу (обязательный)
* `--test-mode` - режим работы с тестовым репозиторием
* `--output-file` - имя файла с графом (по умолчанию dependency\_graph.png)
* `--ascii-tree` - вывод в формате ASCII-дерева
* `--filter` - подстрока для фильтрации пакетов



\## Тесты



Запуск тестов:



```text
python -m pytest tests/ -v
```

