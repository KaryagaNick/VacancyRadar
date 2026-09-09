"""Проверки подготовки вакансий к загрузке в PostgreSQL."""

import unittest

from database import VACANCY_COLUMNS, vacancy_to_row


class DatabaseTests(unittest.TestCase):
    def test_vacancy_to_row_preserves_false_and_zero(self) -> None:
        vacancy = {
            "source": "Example",
            "source_id": 42,
            "remote": False,
            "experience": 0,
            "company": "",
        }

        row = vacancy_to_row(vacancy)
        values = dict(zip(VACANCY_COLUMNS, row))

        self.assertEqual(len(row), len(VACANCY_COLUMNS))
        self.assertEqual(values["source_id"], "42")
        self.assertIs(values["remote"], False)
        self.assertEqual(values["experience"], 0)
        self.assertIsNone(values["company"])


if __name__ == "__main__":
    unittest.main()
