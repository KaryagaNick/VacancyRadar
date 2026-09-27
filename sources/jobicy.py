

from config import (
    INTERNATIONAL_SEARCH_QUERIES,
    JOBICY_API_URL,
    JOBICY_RESULT_LIMIT,
)
from sources.common import request_json
from transform import (
    clean_salary,
    first_present,
    html_to_text,
    join_values,
    normalize_currency,
    normalize_date,
)


def fetch_all(search_text: str) -> list[dict]:

    params = {
        "count": JOBICY_RESULT_LIMIT,
        "geo": "anywhere",
        "tag": search_text,
    }
    data = request_json(JOBICY_API_URL, params)
    jobs = data.get("jobs", [])
    print(f"    Загружено: {len(jobs)}")
    return jobs


def normalize(
    job: dict,
    direction: str,
    search_query: str,
    loaded_at: str,
) -> dict:

    location = join_values(job.get("jobGeo")) or "Worldwide"
    is_worldwide = location.casefold() in {"anywhere", "worldwide"}
    salary_from = first_present(job, "salaryMin", "annualSalaryMin")
    salary_to = first_present(job, "salaryMax", "annualSalaryMax")
    salary_period = job.get("salaryPeriod")
    if salary_period is None and (
        job.get("annualSalaryMin") is not None
        or job.get("annualSalaryMax") is not None
    ):
        salary_period = "annual"

    return {
        "source": "Jobicy",
        "source_id": job.get("id") or job.get("jobSlug") or job.get("url"),
        "direction": direction,
        "search_query": search_query,
        "name": job.get("jobTitle"),
        "company": job.get("companyName"),
        "region": None,
        "location": location,
        "remote": True,
        "remote_scope": "Worldwide" if is_worldwide else "Restricted",
        "timezone_restrictions": None,
        "seniority": job.get("jobLevel"),
        "experience": None,
        "salary_from": clean_salary(salary_from),
        "salary_to": clean_salary(salary_to),
        "currency": normalize_currency(job.get("salaryCurrency")),
        "salary_period": salary_period,
        "employment": join_values(job.get("jobType")),
        "schedule": None,
        "description": html_to_text(job.get("jobDescription")),
        "published_at": normalize_date(job.get("pubDate")),
        "expires_at": None,
        "loaded_at": loaded_at,
        "url": job.get("url"),
    }


def collect_jobicy(loaded_at: str) -> tuple[list[dict], int]:

    vacancies = []
    loaded_count = 0

    for direction, query in INTERNATIONAL_SEARCH_QUERIES.items():
        print(f"  Поиск: {query!r} ({direction})")
        raw_jobs = fetch_all(query)
        loaded_count += len(raw_jobs)
        vacancies.extend(
            normalize(item, direction, query, loaded_at) for item in raw_jobs
        )

    return vacancies, loaded_count
