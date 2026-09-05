import unittest
from app.core.skill_gap import analyze_skill_gap, get_recommendation_for_skill, RECOMMENDATION_CATALOG
from app.routes.matching import skill_gap, SkillGapRequest


class TestSkillGapAnalysis(unittest.TestCase):

    def test_student_has_all_required_skills(self):
        student_skills = ["Python", "FastAPI", "PostgreSQL"]
        required_skills = ["python", "fastapi", "postgresql"]
        result = analyze_skill_gap(student_skills, required_skills)

        self.assertEqual(result["exact_matches"], ["fastapi", "postgresql", "python"])
        self.assertEqual(result["semantic_matches"], [])
        self.assertEqual(result["missing_skills"], [])
        self.assertEqual(result["skill_gap_percentage"], 0.0)
        self.assertEqual(result["recommendations"], [])

    def test_student_has_none_of_required_skills(self):
        student_skills = ["cooking", "woodworking"]
        required_skills = ["docker", "kubernetes"]
        result = analyze_skill_gap(student_skills, required_skills)

        self.assertEqual(result["exact_matches"], [])
        self.assertEqual(result["semantic_matches"], [])
        self.assertEqual(sorted(result["missing_skills"]), ["docker", "kubernetes"])
        self.assertEqual(result["skill_gap_percentage"], 100.0)
        self.assertEqual(len(result["recommendations"]), 2)
        # All recommendations should have high priority
        for rec in result["recommendations"]:
            self.assertEqual(rec["priority"], "high")

    def test_student_has_some_required_skills(self):
        student_skills = ["python", "git"]
        required_skills = ["python", "docker", "postgresql"]
        result = analyze_skill_gap(student_skills, required_skills)

        self.assertEqual(result["exact_matches"], ["python"])
        self.assertEqual(sorted(result["missing_skills"]), ["docker", "postgresql"])
        self.assertAlmostEqual(result["skill_gap_percentage"], 66.67, places=1)
        rec_skills = [r["skill"] for r in result["recommendations"]]
        self.assertIn("docker", rec_skills)
        self.assertIn("postgresql", rec_skills)

    def test_semantic_matches(self):
        student_skills = ["deep learning", "python"]
        required_skills = ["machine learning", "python", "docker"]
        result = analyze_skill_gap(student_skills, required_skills, similarity_threshold=0.55)

        self.assertIn("python", result["exact_matches"])
        # deep learning should semantically match machine learning
        self.assertTrue(len(result["semantic_matches"]) > 0)
        sem_job_skills = [m["job_skill"] for m in result["semantic_matches"]]
        self.assertIn("machine learning", sem_job_skills)
        # docker remains missing
        self.assertIn("docker", result["missing_skills"])
        # Gap should be less than 66.7% due to semantic match credit
        self.assertLess(result["skill_gap_percentage"], 66.7)

    def test_missing_skills_prioritization(self):
        student_skills = ["pandas", "python"]
        required_skills = ["python", "docker", "scikit-learn"]
        # With threshold 0.55, scikit-learn is missing, but has adjacent knowledge from pandas
        result = analyze_skill_gap(student_skills, required_skills, similarity_threshold=0.55)

        self.assertIn("python", result["exact_matches"])
        self.assertIn("docker", result["missing_skills"])
        self.assertIn("scikit-learn", result["missing_skills"])
        # Docker has no related knowledge -> high priority
        # scikit-learn has adjacent knowledge from pandas -> medium priority
        rec_dict = {r["skill"]: r for r in result["recommendations"]}
        self.assertEqual(rec_dict["docker"]["priority"], "high")
        self.assertEqual(rec_dict["scikit-learn"]["priority"], "medium")

    def test_duplicate_skills_handling(self):
        student_skills = ["Python", "python", "PYTHON ", "python 3"]
        required_skills = ["Python", "python 3", "fastapi"]
        result = analyze_skill_gap(student_skills, required_skills)

        # Both student and required should deduplicate to 'python'
        self.assertEqual(result["exact_matches"], ["python"])
        self.assertEqual(result["missing_skills"], ["fastapi"])
        self.assertEqual(result["skill_gap_percentage"], 50.0)

    def test_empty_student_skills(self):
        student_skills = []
        required_skills = ["python", "docker"]
        result = analyze_skill_gap(student_skills, required_skills)

        self.assertEqual(result["exact_matches"], [])
        self.assertEqual(result["semantic_matches"], [])
        self.assertEqual(sorted(result["missing_skills"]), ["docker", "python"])
        self.assertEqual(result["skill_gap_percentage"], 100.0)
        self.assertEqual(len(result["recommendations"]), 2)

    def test_empty_required_skills(self):
        student_skills = ["python", "fastapi"]
        required_skills = []
        result = analyze_skill_gap(student_skills, required_skills)

        self.assertEqual(result["exact_matches"], [])
        self.assertEqual(result["semantic_matches"], [])
        self.assertEqual(result["missing_skills"], [])
        self.assertEqual(result["skill_gap_percentage"], 0.0)
        self.assertEqual(result["recommendations"], [])

    def test_recommendation_generation_catalog(self):
        rec_docker = get_recommendation_for_skill("docker")
        self.assertIn("Docker fundamentals", rec_docker)
        self.assertIn("containers", rec_docker)

        rec_postgres = get_recommendation_for_skill("postgresql")
        self.assertIn("PostgreSQL fundamentals", rec_postgres)
        self.assertIn("SQL queries", rec_postgres)

    def test_unknown_skill_recommendation_fallback(self):
        unknown_skill = "obscure-custom-lib-xyz"
        rec = get_recommendation_for_skill(unknown_skill)
        expected = f"Develop practical experience with {unknown_skill} through documentation, guided projects, and hands-on practice."
        self.assertEqual(rec, expected)

    def test_normalization_integration(self):
        # Case variations, punctuation, aliases should normalize seamlessly
        student_skills = ["ReactJS", "Node.js", "ML/AI"]
        required_skills = ["react.js", "NodeJS", "Machine Learning", "PostgreSQL"]
        result = analyze_skill_gap(student_skills, required_skills)

        self.assertIn("machine learning", result["exact_matches"])
        self.assertIn("node.js", result["exact_matches"])
        self.assertIn("react", result["exact_matches"])
        self.assertEqual(result["missing_skills"], ["postgresql"])
        self.assertEqual(result["skill_gap_percentage"], 25.0)

    def test_route_skill_gap_endpoint(self):
        # Verify the FastAPI route handler directly
        req = SkillGapRequest(
            student_skills=["python"],
            required_skills=["python", "docker"],
            similarity_threshold=0.55
        )
        response = skill_gap(req)
        self.assertIn("exact_matches", response)
        self.assertIn("missing_skills", response)
        self.assertIn("skill_gap_percentage", response)
        self.assertIn("recommendations", response)
        self.assertEqual(response["exact_matches"], ["python"])
        self.assertEqual(response["missing_skills"], ["docker"])
        self.assertEqual(response["skill_gap_percentage"], 50.0)


if __name__ == "__main__":
    unittest.main()
