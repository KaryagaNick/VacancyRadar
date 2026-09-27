# Job Tracker ETL

DE проект для поиска вакансий Python Developer и Data
Engineer(можно настроить под разные направления). Скрипт получает вакансии из открытых API, далее приводит ответы разных
источников к единой схеме и впоследствии сохраняет результат в PostgreSQL. Позволяет быстро и по нужным критериям отобрать вакансию для вас.

## Что уже умеет проект

- получает вакансии с трех платформ «Работы России», Himalayas и Jobicy;
- настроен на поиск вакансий в городе Владивосток, Россия, Приморский край или на удалённой основе
- ищет позиции от стажировки до middle с опытом до двух лет включительно;
- оставляет публикации не старше 90 дней;
- удаляет дубли вакансий внутри одного запуска;
- добавляет новые и обновляет существующие вакансии в PostgreSQL;

## Как движутся данные

API источников
      ↓
Нормализация в общую схему
      ↓
Фильтрация и удаление дублей
      ↓
PostgreSQL

## Стек

- Python 3.10+
- Requests
- Pandas
- PostgreSQL 16
- psycopg2
- Docker

## Алгоритм запуска

1. Создать и активировать виртуальное окружение:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Установить зависимости:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Поднять PostgreSQL:

   ```powershell
   docker compose up -d
   docker compose ps
   ```

4. Запустить ETL-конвейер:

   ```powershell
   python main.py
   ```

Таблица `vacancies` создаётся автоматически. Повторно найденная вакансия
обновляется по уникальной паре `source + source_id`, а не записывается
дополнительной строкой.

## Подключение к PostgreSQL

Параметры локального подключения, в том числе для DBeaver:

Host: `localhost` 
Port: `5433`
Database: `job_tracker`
User: `job_tracker`
Password: `job_tracker`


## Структура проекта

```text
.
├── main.py                 # запуск ETL-конвейера
├── config.py               # запросы, фильтры и подключение
├── transform.py            # очистка, фильтрация и дедупликация
├── database.py             # создание таблицы и upsert в PostgreSQL
├── storage.py              # резервный экспорт в CSV
├── sources/                # отдельный модуль для каждого API
├── sql/init.sql            # схема таблицы и индексы
├── tests/                  # локальные автоматические тесты
├── docker-compose.yml      # локальный PostgreSQL
└── requirements.txt        # Python-зависимости
```

## Источники данных

- [Работа России](https://trudvsem.ru/)
- [Himalayas](https://himalayas.app/)
- [Jobicy](https://jobicy.com/)



