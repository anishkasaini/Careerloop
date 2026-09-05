import unittest
from app.core.normalization import (
    normalize_skill,
    normalize_skill_set,
    normalize_skill_list
)
from app.routes.matching import check_skill_match, MatchingRequest


class TestSkillNormalization(unittest.TestCase):

    def test_normal_skills(self):
        self.assertEqual(normalize_skill("python"), "python")
        self.assertEqual(normalize_skill("html"), "html")
        self.assertEqual(normalize_skill("css"), "css")

    def test_capitalization_and_whitespace(self):
        self.assertEqual(normalize_skill("Python"), "python")
        self.assertEqual(normalize_skill(" PYTHON "), "python")
        self.assertEqual(normalize_skill("\tJavaScript\n"), "javascript")

    def test_aliases_and_variations(self):
        # Python
        self.assertEqual(normalize_skill("Python 3"), "python")
        self.assertEqual(normalize_skill("python programming"), "python")
        self.assertEqual(normalize_skill("py"), "python")

        # Machine Learning / AI
        self.assertEqual(normalize_skill("ML"), "machine learning")
        self.assertEqual(normalize_skill("ML/AI"), "machine learning")
        self.assertEqual(normalize_skill("AI/ML"), "machine learning")

        # JavaScript
        self.assertEqual(normalize_skill("JS"), "javascript")
        self.assertEqual(normalize_skill("JavaScript"), "javascript")

        # React
        self.assertEqual(normalize_skill("ReactJS"), "react")
        self.assertEqual(normalize_skill("React.js"), "react")

        # Node.js
        self.assertEqual(normalize_skill("Node"), "node.js")
        self.assertEqual(normalize_skill("NodeJS"), "node.js")
        self.assertEqual(normalize_skill("Node.js"), "node.js")

        # Postgres
        self.assertEqual(normalize_skill("Postgres"), "postgresql")
        self.assertEqual(normalize_skill("PostgreSQL"), "postgresql")

        # Scikit-learn
        self.assertEqual(normalize_skill("sklearn"), "scikit-learn")
        self.assertEqual(normalize_skill("scikit learn"), "scikit-learn")
        self.assertEqual(normalize_skill("scikit-learn"), "scikit-learn")

    def test_punctuation_sensitive_skills(self):
        self.assertEqual(normalize_skill("C++"), "c++")
        self.assertEqual(normalize_skill("cpp"), "c++")
        self.assertEqual(normalize_skill("C#"), "c#")
        self.assertEqual(normalize_skill("csharp"), "c#")
        self.assertEqual(normalize_skill(".NET"), ".net")
        self.assertEqual(normalize_skill("dotnet"), ".net")

    def test_duplicate_skills_and_set_normalization(self):
        input_skills = ["Python 3", "python", "py", "JS", "JavaScript", "ReactJS", "React.js"]
        normalized_set = normalize_skill_set(input_skills)
        self.assertEqual(normalized_set, {"python", "javascript", "react"})

        sorted_list = normalize_skill_list(input_skills)
        self.assertEqual(sorted_list, ["javascript", "python", "react"])

    def test_matching_endpoint_integration(self):
        request_data = MatchingRequest(
            student_skills=[" Python 3 ", "JS", "ReactJS", "Postgres", "C++"],
            required_skills=["python", "javascript", "react", "postgresql", "c++", "Node"]
        )

        response = check_skill_match(request_data)

        self.assertEqual(response["match_percentage"], 83.33)
        self.assertEqual(
            response["matched_skills"],
            ["c++", "javascript", "postgresql", "python", "react"]
        )
        self.assertEqual(response["missing_skills"], ["node.js"])


if __name__ == "__main__":
    unittest.main()
