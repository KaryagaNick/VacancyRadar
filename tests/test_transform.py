"""Проверки очистки, фильтрации и удаления дублей."""

import unittest

from transform import (
    clean_experience,
    clean_salary,
    deduplicate_vacancies,
    html_to_text,
    is_allowed_seniority,
    matches_location_criteria,
)


class TransformTests(unittest.TestCase):
    def test_html_to_text_removes_tags_and_extra_spaces(self) -> None:
        self.assertEqual(html_to_text("<p>Hello <b>Python</b></p>"), "Hello Python")

    def test_clean_salary_keeps_positive_number(self) -> None:
        self.assertEqual(clean_salary("120 000"), 120000)
        self.assertIsNone(clean_salary(0))

    def test_clean_experience_keeps_zero(self) -> None:
        self.assertEqual(clean_experience(0), 0)
        self.assertEqual(clean_experience("2"), 2)

    def test_remote_or_vladivostok_matches_location(self) -> None:
        self.assertTrue(matches_location_criteria({"remote": True}))
        self.assertTrue(
            matches_location_criteria(
                {"remote": False, "location": "Владивосток", "region": None}
            )
        )
        self.assertFalse(
            matches_location_criteria(
                {"remote": False, "location": "Москва", "region": None}
            )
        )

    def test_seniority_above_middle_is_rejected(self) -> None:
        self.assertTrue(is_allowed_seniority("Entry-level; Mid-level"))
        self.assertFalse(is_allowed_seniority("Mid-level; Senior"))
        self.assertFalse(is_allowed_seniority("Lead"))

    def test_deduplication_merges_search_metadata(self) -> None:
        first = {
            "source": "Example",
            "source_id": "1",
            "direction": "python_developer",
            "search_query": "python developer",
        }
        second = {
            **first,
            "direction": "data_engineer",
            "search_query": "data engineer",
        }

        result = deduplicate_vacancies([first, second])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["direction"], "python_developer; data_engineer")
        self.assertEqual(
            result[0]["search_query"], "python developer; data engineer"
        )


if __name__ == "__main__":
    unittest.main()
