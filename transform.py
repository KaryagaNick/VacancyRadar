from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from config import (
    EXCLUDED_TITLE_WORDS,
    MAX_EXPERIENCE,
    MAX_VACANCY_AGE_DAYS,
    RELEVANCE_KEYWORDS,
    REMOTE_KEYWORDS,
    TARGET_CITY,
)


class HTMLTextExtractor(HTMLParser):
    """HTML-парсер"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())


def html_to_text(value: str | None) -> str | None:
    """Удалять теги HTML из описания международной вакансии"""
    if not value:
        return None

    parser = HTMLTextExtractor()
    parser.feed(str(value))
    text = " ".join(parser.parts)
    return " ".join(text.split()) or None


def clean_salary(value: int | float | str | None) -> int | float | None:
    """Преобразовать зарплату"""
    if value in (None, "", 0, "0"):
        return None

    try:
        number = float(str(value).replace(" ", "").replace(",", "."))
    except (TypeError, ValueError):
        return None

    if number <= 0:
        return None
    if number.is_integer():
        return int(number)
    return number


def clean_experience(value: int | float | str | None) -> int | None:
    """Преобразовать опыт в число"""
    if value in (None, ""):
        return None

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def normalize_currency(value: str | None) -> str | None:
    """Привести валюты к единому виду"""
    if value is None:
        return None

    currency = str(value).strip()
    if "руб" in currency.lower() or currency.upper() in {"RUB", "RUR"}:
        return "RUB"
    return currency.upper() or None


def normalize_date(value: str | int | float | None) -> str | None:
    """Преобразовать дату"""
    if value in (None, ""):
        return None

    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value, timezone.utc).date().isoformat()
        except (OSError, OverflowError, ValueError):
            return None

    text = str(value).strip()
    if text.isdigit() and len(text) >= 10:
        try:
            return datetime.fromtimestamp(int(text), timezone.utc).date().isoformat()
        except (OSError, OverflowError, ValueError):
            return None

    try:
        return date.fromisoformat(text[:10]).isoformat()
    except ValueError:
        return None


def join_values(value: object) -> str | None:
    """Преобразовать список значений API в одну читаемую строку"""
    if isinstance(value, list):
        items = [str(item) for item in value if item not in (None, "")]
        return "; ".join(items) or None
    if value in (None, ""):
        return None
    return str(value)


def first_present(data: dict, *keys: str) -> object | None:
    """Взять первое существующую запись из нескольких вариантов"""
    for key in keys:
        value = data.get(key)
        if value not in (None, ""):
            return value
    return None


def is_remote_format(employment: object, schedule: object) -> bool:
    """Определить удалённый формат по текстовым полям вакансии"""
    work_format = f"{employment or ''} {schedule or ''}".lower()
    return any(keyword in work_format for keyword in REMOTE_KEYWORDS)


def is_recent(published_at: str | None, max_age_days: int) -> bool:
    """Проверить, что вакансия опубликована не слишком давно"""
    if published_at is None:
        return False

    published_date = date.fromisoformat(published_at)
    cutoff_date = date.today() - timedelta(days=max_age_days)
    return published_date >= cutoff_date


def matches_location_criteria(vacancy: dict) -> bool:
    """Либо удаленка либо Владивосток"""
    if vacancy.get("remote") is True:
        return True

    place = " ".join(
        str(vacancy.get(field) or "") for field in ("location", "region")
    ).lower()
    return TARGET_CITY in place


def is_allowed_seniority(value: str | None) -> bool:
    """Отсеять уровни выше middle"""
    if not value:
        return True

    seniority = value.lower()
    excluded = ("senior", "lead", "staff", "principal", "manager", "director")
    return not any(word in seniority for word in excluded)


def is_suitable_vacancy(vacancy: dict) -> bool:
    """Оставить свежие вакансии до middle включительно"""
    title = str(vacancy.get("name") or "").lower()
    description = str(vacancy.get("description") or "").lower()
    experience = vacancy.get("experience")
    direction = vacancy.get("direction")

    if any(word in title for word in EXCLUDED_TITLE_WORDS):
        return False
    if experience is not None and experience > MAX_EXPERIENCE:
        return False
    if not is_allowed_seniority(vacancy.get("seniority")):
        return False
    if not is_recent(vacancy.get("published_at"), MAX_VACANCY_AGE_DAYS):
        return False
    if not matches_location_criteria(vacancy):
        return False

    keywords = RELEVANCE_KEYWORDS.get(direction, ())
    searchable_text = f"{title} {description}"
    return any(keyword in searchable_text for keyword in keywords)


def merge_text_values(first: str, second: str) -> str:
    """Объединить текстовые метки без повторов"""
    values = first.split("; ")
    if second not in values:
        values.append(second)
    return "; ".join(values)


def deduplicate_vacancies(vacancies: list[dict]) -> list[dict]:
    """Удалить повторы внутри источника по его id"""
    unique_vacancies = {}

    for vacancy in vacancies:
        identity = vacancy.get("source_id") or vacancy.get("url")
        if identity is None:
            continue

        key = (vacancy["source"], str(identity))
        if key not in unique_vacancies:
            unique_vacancies[key] = vacancy.copy()
            continue

        existing = unique_vacancies[key]
        existing["direction"] = merge_text_values(
            existing["direction"], vacancy["direction"]
        )
        existing["search_query"] = merge_text_values(
            existing["search_query"], vacancy["search_query"]
        )

    return list(unique_vacancies.values())
