import sys
from datetime import datetime, timezone

import requests

from config import OUTPUT_FILE
from database import DatabaseError, save_to_postgres
from sources import collect_himalayas, collect_jobicy, collect_trudvsem
from storage import save_to_csv
from transform import deduplicate_vacancies, is_suitable_vacancy


def main() -> None:
    
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    loaded_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    collectors = (
        ("Работа России", collect_trudvsem),
        ("Himalayas", collect_himalayas),
        ("Jobicy", collect_jobicy),
    )

    all_vacancies = []
    total_loaded = 0
    failed_sources = []

    for source_name, collector in collectors:
        print(f"\nИсточник: {source_name}")
        try:
            normalized, loaded_count = collector(loaded_at)
        except (requests.RequestException, ValueError, TypeError, KeyError) as error:
            failed_sources.append(source_name)
            print(f"  Источник временно недоступен: {error}")
            continue

        suitable = [item for item in normalized if is_suitable_vacancy(item)]
        all_vacancies.extend(suitable)
        total_loaded += loaded_count
        print(f"  Получено до фильтров: {loaded_count}")
        print(f"  Подходящих после фильтров: {len(suitable)}")

    vacancies = deduplicate_vacancies(all_vacancies)
    duplicate_count = len(all_vacancies) - len(vacancies)

    print(f"\nПолучено записей до фильтров: {total_loaded}")
    print(f"Подходящих записей до удаления повторов: {len(all_vacancies)}")
    print(f"Удалено повторов внутри источников: {duplicate_count}")
    print(f"Итоговых уникальных вакансий: {len(vacancies)}")

    if failed_sources:
        print(f"Недоступные источники: {', '.join(failed_sources)}")

    if not vacancies:
        print("Подходящих вакансий нет. Старый CSV не был перезаписан.")
        return

    try:
        saved_count = save_to_postgres(vacancies)
        print(f"Добавлено или обновлено в PostgreSQL: {saved_count}")
    except (DatabaseError, UnicodeError) as error:
        reason = str(error).splitlines()[0]
        print(f"Не удалось сохранить данные в PostgreSQL: {reason}")
        print("Проверьте, что Docker запущен: docker compose up -d")

    try:
        save_to_csv(vacancies)
    except PermissionError:
        print(
            "Не удалось сохранить CSV: файл vacancies.csv открыт "
            "в другой программе. Закройте его и запустите скрипт снова."
        )
    else:
        print(f"Резервная CSV-копия сохранена в: {OUTPUT_FILE}")

    print("Источники: trudvsem.ru, himalayas.app, jobicy.com")


if __name__ == "__main__":
    main()
