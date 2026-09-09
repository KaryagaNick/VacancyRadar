"""Создание таблицы и сохранение вакансий в PostgreSQL."""

import psycopg2
from psycopg2 import Error as DatabaseError
from psycopg2.extras import execute_values

from config import (
    DATABASE_SCHEMA_FILE,
    DB_CONNECT_TIMEOUT_SECONDS,
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
)


VACANCY_COLUMNS = (
    "source",
    "source_id",
    "direction",
    "search_query",
    "name",
    "company",
    "region",
    "location",
    "remote",
    "remote_scope",
    "timezone_restrictions",
    "seniority",
    "experience",
    "salary_from",
    "salary_to",
    "currency",
    "salary_period",
    "employment",
    "schedule",
    "description",
    "published_at",
    "expires_at",
    "loaded_at",
    "url",
)

UPSERT_VACANCIES_SQL = """
    INSERT INTO vacancies (
        source, source_id, direction, search_query, name, company, region,
        location, remote, remote_scope, timezone_restrictions, seniority,
        experience, salary_from, salary_to, currency, salary_period,
        employment, schedule, description, published_at, expires_at,
        loaded_at, url
    )
    VALUES %s
    ON CONFLICT (source, source_id) DO UPDATE SET
        direction = EXCLUDED.direction,
        search_query = EXCLUDED.search_query,
        name = EXCLUDED.name,
        company = EXCLUDED.company,
        region = EXCLUDED.region,
        location = EXCLUDED.location,
        remote = EXCLUDED.remote,
        remote_scope = EXCLUDED.remote_scope,
        timezone_restrictions = EXCLUDED.timezone_restrictions,
        seniority = EXCLUDED.seniority,
        experience = EXCLUDED.experience,
        salary_from = EXCLUDED.salary_from,
        salary_to = EXCLUDED.salary_to,
        currency = EXCLUDED.currency,
        salary_period = EXCLUDED.salary_period,
        employment = EXCLUDED.employment,
        schedule = EXCLUDED.schedule,
        description = EXCLUDED.description,
        published_at = EXCLUDED.published_at,
        expires_at = EXCLUDED.expires_at,
        loaded_at = EXCLUDED.loaded_at,
        url = EXCLUDED.url
"""


def empty_to_none(value: object) -> object | None:
    """Преобразовать пустую строку в SQL NULL, сохранив False и 0."""
    return None if value in (None, "") else value


def vacancy_to_row(vacancy: dict) -> tuple:
    """Собрать значения вакансии в порядке столбцов таблицы."""
    values = []
    for column in VACANCY_COLUMNS:
        value = vacancy.get(column)
        if column == "source_id" and value is not None:
            value = str(value)
        values.append(empty_to_none(value))
    return tuple(values)


def save_to_postgres(vacancies: list[dict]) -> int:
    """Создать таблицу при необходимости и добавить или обновить вакансии."""
    rows = [vacancy_to_row(vacancy) for vacancy in vacancies]
    if not rows:
        return 0

    schema_sql = DATABASE_SCHEMA_FILE.read_text(encoding="utf-8")
    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=DB_CONNECT_TIMEOUT_SECONDS,
    )

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(schema_sql)
                execute_values(cursor, UPSERT_VACANCIES_SQL, rows, page_size=100)
    finally:
        connection.close()

    return len(rows)
