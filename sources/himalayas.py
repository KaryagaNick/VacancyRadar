"""Получение международных remote-вакансий через Himalayas."""

import time

from config import (
    HIMALAYAS_API_URL,
    HIMALAYAS_MAX_PAGES,
    HIMALAYAS_SENIORITIES,
    INTERNATIONAL_SEARCH_QUERIES,
    REQUEST_DELAY_SECONDS,
)
from sources.common import request_json
from transform import (
    clean_salary,
    html_to_text,
    join_values,
    normalize_currency,
    normalize_date,
)


def fetch_all(search_text: str, seniority: str) -> list[dict]:
    """Получить worldwide-вакансии с постраничной загрузкой."""
    all_jobs = []

    for page_number in range(1, HIMALAYAS_MAX_PAGES + 1):
        params = {
            "q": search_text,
            "worldwide": "true",
            "seniority": seniority,
            "sort": "recent",
            "page": page_number,
        }
        data = request_json(HIMALAYAS_API_URL, params)
        page_jobs = data.get("jobs", [])
        total = int(data.get("totalCount", len(page_jobs)))
        all_jobs.extend(page_jobs)
        print(f"    Загружено: {len(all_jobs)} из {total}")

        page_limit = int(data.get("limit", 20))
        if not page_jobs or len(all_jobs) >= total or len(page_jobs) < page_limit:
            return all_jobs

        time.sleep(REQUEST_DELAY_SECONDS)

    print(f"    Достигнут лимит: {HIMALAYAS_MAX_PAGES} страниц на запрос")
    return all_jobs


def normalize(
    job: dict,
    direction: str,
    search_query: str,
    loaded_at: str,
) -> dict:
    """Привести вакансию к общей схеме проекта."""
    locations = join_values(job.get("locationRestrictions"))

    return {
        "source": "Himalayas",
        "source_id": job.get("guid") or job.get("applicationLink"),
        "direction": direction,
        "search_query": search_query,
        "name": job.get("title"),
        "company": job.get("companyName"),
        "region": None,
        "location": locations or "Worldwide",
        "remote": True,
        "remote_scope": "Restricted" if locations else "Worldwide",
        "timezone_restrictions": join_values(job.get("timezoneRestrictions")),
        "seniority": join_values(job.get("seniority")),
        "experience": None,
        "salary_from": clean_salary(job.get("minSalary")),
        "salary_to": clean_salary(job.get("maxSalary")),
        "currency": normalize_currency(job.get("currency")),
        "salary_period": job.get("salaryPeriod"),
        "employment": job.get("employmentType"),
        "schedule": None,
        "description": html_to_text(job.get("description")),
        "published_at": normalize_date(job.get("pubDate")),
        "expires_at": normalize_date(job.get("expiryDate")),
        "loaded_at": loaded_at,
        "url": job.get("applicationLink"),
    }


def collect_himalayas(loaded_at: str) -> tuple[list[dict], int]:
    """Загрузить и нормализовать все настроенные запросы источника."""
    vacancies = []
    loaded_count = 0

    for direction, query in INTERNATIONAL_SEARCH_QUERIES.items():
        for seniority in HIMALAYAS_SENIORITIES:
            print(f"  Поиск: {query!r}, {seniority} ({direction})")
            raw_jobs = fetch_all(query, seniority)
            loaded_count += len(raw_jobs)
            vacancies.extend(
                normalize(item, direction, query, loaded_at) for item in raw_jobs
            )

    return vacancies, loaded_count
