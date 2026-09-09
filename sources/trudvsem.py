"""Получение вакансий через API «Работа России»."""

import time

from config import (
    MAX_EXPERIENCE,
    REQUEST_DELAY_SECONDS,
    TRUDVSEM_API_URL,
    TRUDVSEM_PAGE_SIZE,
    TRUDVSEM_SEARCH_QUERIES,
)
from sources.common import request_json
from transform import (
    clean_experience,
    clean_salary,
    is_remote_format,
    normalize_currency,
    normalize_date,
)


def extract_location(vacancy: dict) -> str | None:
    """Собрать населённые пункты из блока адресов вакансии."""
    addresses = vacancy.get("addresses") or {}

    if isinstance(addresses, dict):
        address_items = addresses.get("address") or []
    elif isinstance(addresses, list):
        address_items = addresses
    else:
        address_items = []

    if isinstance(address_items, dict):
        address_items = [address_items]

    locations = []
    for address in address_items:
        if not isinstance(address, dict):
            continue
        location = address.get("location")
        if location and location not in locations:
            locations.append(str(location))

    return "; ".join(locations) or None


def fetch_page(search_text: str, page_number: int) -> tuple[list[dict], int]:
    """Получить одну страницу вакансий."""
    params = {
        "text": search_text,
        "limit": TRUDVSEM_PAGE_SIZE,
        "offset": page_number,
        "experienceTo": MAX_EXPERIENCE,
    }
    data = request_json(TRUDVSEM_API_URL, params)

    if str(data.get("status")) != "200":
        raise ValueError(f"Работа России вернула неожиданный ответ: {data}")

    items = data.get("results", {}).get("vacancies", [])
    total = int(data.get("meta", {}).get("total", 0))
    vacancies = [item["vacancy"] for item in items if "vacancy" in item]
    return vacancies, total


def fetch_all(search_text: str) -> list[dict]:
    """Получить все страницы по одному поисковому запросу."""
    all_vacancies = []
    page_number = 0

    while True:
        page_vacancies, total = fetch_page(search_text, page_number)
        all_vacancies.extend(page_vacancies)
        print(f"    Загружено: {len(all_vacancies)} из {total}")

        if not page_vacancies or len(all_vacancies) >= total:
            break

        page_number += 1
        time.sleep(REQUEST_DELAY_SECONDS)

    return all_vacancies


def normalize(
    vacancy: dict,
    direction: str,
    search_query: str,
    loaded_at: str,
) -> dict:
    """Привести вакансию к общей схеме проекта."""
    company = vacancy.get("company") or {}
    region = vacancy.get("region") or {}
    requirement = vacancy.get("requirement") or {}
    employment = vacancy.get("employment")
    schedule = vacancy.get("schedule")
    remote = is_remote_format(employment, schedule)

    return {
        "source": "Работа России",
        "source_id": vacancy.get("id"),
        "direction": direction,
        "search_query": search_query,
        "name": vacancy.get("job-name"),
        "company": company.get("name"),
        "region": region.get("name"),
        "location": extract_location(vacancy),
        "remote": remote,
        "remote_scope": "Russia" if remote else None,
        "timezone_restrictions": None,
        "seniority": None,
        "experience": clean_experience(requirement.get("experience")),
        "salary_from": clean_salary(vacancy.get("salary_min")),
        "salary_to": clean_salary(vacancy.get("salary_max")),
        "currency": normalize_currency(vacancy.get("currency")),
        "salary_period": None,
        "employment": employment,
        "schedule": schedule,
        "description": vacancy.get("duty"),
        "published_at": normalize_date(vacancy.get("creation-date")),
        "expires_at": None,
        "loaded_at": loaded_at,
        "url": vacancy.get("vac_url"),
    }


def collect_trudvsem(loaded_at: str) -> tuple[list[dict], int]:
    """Загрузить и нормализовать все настроенные запросы источника."""
    vacancies = []
    loaded_count = 0

    for direction, queries in TRUDVSEM_SEARCH_QUERIES.items():
        for query in queries:
            print(f"  Поиск: {query!r} ({direction})")
            raw_vacancies = fetch_all(query)
            loaded_count += len(raw_vacancies)
            vacancies.extend(
                normalize(item, direction, query, loaded_at)
                for item in raw_vacancies
            )

    return vacancies, loaded_count
