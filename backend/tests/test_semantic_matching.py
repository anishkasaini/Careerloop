import unittest
from app.core.semantic_matching import compute_semantic_matching


class TestSemanticMatching(unittest.TestCase):

    def test_exact_matches(self):
        student_skills = ["Python", "FastAPI", "PostgreSQL"]
        required_skills = ["python", "fastapi", "postgresql"]
        result = compute_semantic_matching(student_skills, required_skills)

        self.assertEqual(result["exact_matches"], ["fastapi", "postgresql", "python"])
        self.assertEqual(result["semantic_matches"], [])
        self.assertEqual(result["unmatched_required_skills"], [])
        self.assertEqual(result["exact_match_score"], 1.0)
        self.assertEqual(result["combined_match_score"], 1.0)

    def test_semantic_related_matches(self):
        student_skills = ["scikit-learn", "python"]
        required_skills = ["machine learning", "python"]
        result = compute_semantic_matching(student_skills, required_skills, similarity_threshold=0.35)

        self.assertIn("python", result["exact_matches"])
        self.assertEqual(len(result["semantic_matches"]), 1)
        sem_match = result["semantic_matches"][0]
        self.assertEqual(sem_match["job_skill"], "machine learning")
        self.assertEqual(sem_match["student_skill"], "scikit-learn")
        self.assertGreaterEqual(sem_match["similarity_score"], 0.35)
        self.assertGreater(result["combined_match_score"], result["exact_match_score"])

    def test_deep_learning_semantic_match(self):
        student_skills = ["deep learning", "python"]
        required_skills = ["machine learning", "python"]
        result = compute_semantic_matching(student_skills, required_skills, similarity_threshold=0.55)

        self.assertIn("python", result["exact_matches"])
        self.assertTrue(len(result["semantic_matches"]) > 0)
        sem_match = result["semantic_matches"][0]
        self.assertEqual(sem_match["job_skill"], "machine learning")
        self.assertEqual(sem_match["student_skill"], "deep learning")

    def test_no_match(self):
        student_skills = ["cooking", "gardening"]
        required_skills = ["kubernetes", "aws"]
        result = compute_semantic_matching(student_skills, required_skills, similarity_threshold=0.75)

        self.assertEqual(result["exact_matches"], [])
        self.assertEqual(result["semantic_matches"], [])
        self.assertEqual(result["unmatched_required_skills"], ["aws", "kubernetes"])
        self.assertEqual(result["exact_match_score"], 0.0)
        self.assertEqual(result["combined_match_score"], 0.0)

    def test_empty_inputs(self):
        result = compute_semantic_matching([], [])
        self.assertEqual(result["exact_matches"], [])
        self.assertEqual(result["semantic_matches"], [])
        self.assertEqual(result["unmatched_required_skills"], [])
        self.assertEqual(result["exact_match_score"], 0.0)
        self.assertEqual(result["combined_match_score"], 0.0)

    def test_high_threshold_prevents_semantic_match(self):
        student_skills = ["django"]
        required_skills = ["react"]
        result = compute_semantic_matching(student_skills, required_skills, similarity_threshold=0.95)

        self.assertEqual(result["exact_matches"], [])
        self.assertEqual(result["semantic_matches"], [])
        self.assertEqual(result["unmatched_required_skills"], ["react"])


if __name__ == "__main__":
    unittest.main()
