import unittest
from app.core.extraction import extract_skills_from_text
from app.routes.skills import extract_skills


class TestJobDescriptionSkillExtraction(unittest.TestCase):

    def test_simple_jd_extraction(self):
        jd_text = (
            "We are looking for a Python Backend Developer. The candidate should "
            "have experience with FastAPI, REST APIs, SQL, PostgreSQL, Docker, "
            "Git and machine learning. Knowledge of AWS is a plus."
        )
        extracted = extract_skills_from_text(jd_text)
        expected = [
            "aws", "docker", "fastapi", "git", "machine learning",
            "postgresql", "python", "rest api", "sql"
        ]
        self.assertEqual(extracted, expected)

    def test_capitalization_and_whitespace(self):
        jd = "Seeking developers with PYTHON, FastApi, DOCKER, and AWS experience."
        extracted = extract_skills_from_text(jd)
        self.assertEqual(extracted, ["aws", "docker", "fastapi", "python"])

    def test_multi_word_skills(self):
        jd = (
            "Roles require expertise in Machine Learning, Deep Learning, "
            "Data Science, Natural Language Processing, Computer Vision, "
            "REST APIs and Scikit-Learn."
        )
        extracted = extract_skills_from_text(jd)
        expected = [
            "computer vision", "data science", "deep learning",
            "machine learning", "natural language processing",
            "rest api", "scikit-learn"
        ]
        self.assertEqual(extracted, expected)

    def test_aliases_in_jd(self):
        jd = "Looking for developers with ML, JS, ReactJS, NodeJS, Postgres and sklearn."
        extracted = extract_skills_from_text(jd)
        expected = [
            "javascript", "machine learning", "node.js",
            "postgresql", "react", "scikit-learn"
        ]
        self.assertEqual(extracted, expected)

    def test_duplicate_skills_deduplication(self):
        jd = "Python, python, Python 3, py, JS, JavaScript, React, React.js"
        extracted = extract_skills_from_text(jd)
        self.assertEqual(extracted, ["javascript", "python", "react"])

    def test_sql_false_positives_prevention(self):
        # Case A: Only MySQL and PostgreSQL mentioned (SQL standalone is NOT present)
        jd1 = "We use MySQL and PostgreSQL database clusters."
        extracted1 = extract_skills_from_text(jd1)
        self.assertIn("mysql", extracted1)
        self.assertIn("postgresql", extracted1)
        self.assertNotIn("sql", extracted1)

        # Case B: SQL is mentioned standalone alongside PostgreSQL
        jd2 = "Candidates should know SQL and PostgreSQL."
        extracted2 = extract_skills_from_text(jd2)
        self.assertIn("sql", extracted2)
        self.assertIn("postgresql", extracted2)

        # Case C: SQLite mentioned without SQL
        jd3 = "Embedded storage uses SQLite."
        extracted3 = extract_skills_from_text(jd3)
        self.assertIn("sqlite", extracted3)
        self.assertNotIn("sql", extracted3)

    def test_special_character_skills(self):
        jd = "Experience with C++, C#, .NET, Node.js, and React.js is mandatory."
        extracted = extract_skills_from_text(jd)
        expected = [".net", "c#", "c++", "node.js", "react"]
        self.assertEqual(extracted, expected)

    def test_absent_skills(self):
        jd = "We need an HR Manager for recruitment, payroll, and event management."
        extracted = extract_skills_from_text(jd)
        self.assertEqual(extracted, [])

    def test_resume_extraction_backward_compatibility(self):
        text = "Resume highlights: Python, FastAPI, Docker, and ML experience."
        extracted = extract_skills(text)
        self.assertEqual(extracted, ["docker", "fastapi", "machine learning", "python"])


if __name__ == "__main__":
    unittest.main()
