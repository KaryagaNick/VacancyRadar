import os
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = PROJECT_DIR / "data" / "vacancies.csv"
DATABASE_SCHEMA_FILE = PROJECT_DIR / "sql" / "init.sql"

# Значения по умолчанию совпадают с docker-compose.yml. Их можно переопределить
# переменными окружения, не меняя исходный код.
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5433"))
DB_NAME = os.getenv("POSTGRES_DB", "job_tracker")
DB_USER = os.getenv("POSTGRES_USER", "job_tracker")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "job_tracker")
DB_CONNECT_TIMEOUT_SECONDS = 5

TRUDVSEM_API_URL = "https://opendata.trudvsem.ru/api/v1/vacancies"
HIMALAYAS_API_URL = "https://himalayas.app/jobs/api/search"
JOBICY_API_URL = "https://jobicy.com/api/v2/remote-jobs"

HTTP_TIMEOUT_SECONDS = 30
REQUEST_DELAY_SECONDS = 0.2
TRUDVSEM_PAGE_SIZE = 100
HIMALAYAS_MAX_PAGES = 10
JOBICY_RESULT_LIMIT = 200

HEADERS = {"User-Agent": "JobTrackerStudentProject/0.2"}

TRUDVSEM_SEARCH_QUERIES = {
    "python_developer": (
        "Python разработчик",
        "Программист Python",
        "Backend Python",
        "Стажер Python",
    ),
    "data_engineer": (
        "Data Engineer",
        "Инженер данных",
        "Разработчик ETL",
        "Стажер Data Engineer",
    ),
}

INTERNATIONAL_SEARCH_QUERIES = {
    "python_developer": "python developer",
    "data_engineer": "data engineer",
}
HIMALAYAS_SENIORITIES = ("Entry-level", "Mid-level")

# Критерии: от стажировки до middle включительно.
MAX_EXPERIENCE = 2
MAX_VACANCY_AGE_DAYS = 90
TARGET_CITY = "владивосток"
REMOTE_KEYWORDS = ("дистанцион", "удален", "remote")
EXCLUDED_TITLE_WORDS = (
    "senior",
    "lead",
    "staff",
    "principal",
    "director",
    "head of",
    "chief",
    "старший",
    "ведущий",
    "главный",
    "руководитель",
)
RELEVANCE_KEYWORDS = {
    "python_developer": ("python",),
    "data_engineer": ("data engineer", "инженер данных", "etl", "dwh"),
}
