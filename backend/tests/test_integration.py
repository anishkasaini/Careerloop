import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.core.skill_gap import analyze_skill_gap
from app.core.extraction import extract_skills_from_text


class TestCareerLoopIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_end_to_end_scenario(self):
        """
        Scenario from requirement:
        Student: Python, Machine Learning, Pandas, Git
        Job: Python, Machine Learning, Scikit-learn, Docker, Git
        """
        student_skills = ["Python", "Machine Learning", "Pandas", "Git"]
        job_skills = ["Python", "Machine Learning", "Scikit-learn", "Docker", "Git"]

        # Call endpoint
        response = self.client.post(
            "/matching/skill-gap",
            json={
                "student_skills": student_skills,
                "required_skills": job_skills,
                "similarity_threshold": 0.55
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # 1. Exact matches: git, machine learning, python
        self.assertIn("git", data["exact_matches"])
        self.assertIn("machine learning", data["exact_matches"])
        self.assertIn("python", data["exact_matches"])
        self.assertEqual(len(data["exact_matches"]), 3)

        # 2. Missing skills: docker must be missing
        self.assertIn("docker", data["missing_skills"])

        # 3. Skill gap percentage
        self.assertGreater(data["skill_gap_percentage"], 0.0)
        self.assertLess(data["skill_gap_percentage"], 100.0)

        # 4. Learning recommendations
        self.assertGreater(len(data["recommendations"]), 0)
        rec_skills = [r["skill"] for r in data["recommendations"]]
        self.assertIn("docker", rec_skills)

        # Verify docker recommendation content
        docker_rec = next(r for r in data["recommendations"] if r["skill"] == "docker")
        self.assertIn(docker_rec["priority"], ["high", "medium"])
        self.assertIn("Docker fundamentals", docker_rec["recommendation"])

    def test_end_to_end_with_semantic_threshold(self):
        """
        With a configured threshold (0.40), scikit-learn and pandas are semantically linked.
        """
        student_skills = ["Python", "Machine Learning", "Pandas", "Git"]
        job_skills = ["Python", "Machine Learning", "Scikit-learn", "Docker", "Git"]

        response = self.client.post(
            "/matching/skill-gap",
            json={
                "student_skills": student_skills,
                "required_skills": job_skills,
                "similarity_threshold": 0.40
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # scikit-learn should appear in semantic_matches
        self.assertTrue(len(data["semantic_matches"]) > 0)
        sem_job = [m["job_skill"] for m in data["semantic_matches"]]
        self.assertIn("scikit-learn", sem_job)

        # docker remains missing
        self.assertIn("docker", data["missing_skills"])

    def test_resume_text_to_skill_gap_pipeline(self):
        """
        Simulate full flow: Raw Resume text -> Extracted Skills -> Job Skill Gap.
        """
        raw_resume = """
        Experienced Backend Software Engineer.
        Proficient in Python programming, FastAPI, Docker, and PostgreSQL.
        Knowledge of Git version control and REST API architecture.
        """
        # Step 1: Extract skills from resume
        extracted_student_skills = extract_skills_from_text(raw_resume)
        self.assertIn("python", extracted_student_skills)
        self.assertIn("fastapi", extracted_student_skills)
        self.assertIn("docker", extracted_student_skills)

        # Step 2: Compare with Machine Learning Engineer JD
        job_required = ["Python", "FastAPI", "Kubernetes", "AWS"]

        res = analyze_skill_gap(extracted_student_skills, job_required)
        self.assertIn("python", res["exact_matches"])
        self.assertIn("fastapi", res["exact_matches"])
        self.assertIn("kubernetes", res["missing_skills"])
        self.assertIn("aws", res["missing_skills"])
        self.assertEqual(res["skill_gap_percentage"], 50.0)

    def test_empty_student_skills_flow(self):
        response = self.client.post(
            "/matching/skill-gap",
            json={"student_skills": [], "required_skills": ["docker", "python"]}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["exact_matches"], [])
        self.assertEqual(sorted(data["missing_skills"]), ["docker", "python"])
        self.assertEqual(data["skill_gap_percentage"], 100.0)

    def test_empty_required_skills_flow(self):
        response = self.client.post(
            "/matching/skill-gap",
            json={"student_skills": ["python"], "required_skills": []}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["skill_gap_percentage"], 0.0)
        self.assertEqual(data["missing_skills"], [])

    def test_all_skills_matched_flow(self):
        response = self.client.post(
            "/matching/skill-gap",
            json={"student_skills": ["Python 3", "Docker"], "required_skills": ["python", "docker"]}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["skill_gap_percentage"], 0.0)
        self.assertEqual(data["missing_skills"], [])
        self.assertEqual(data["recommendations"], [])

    def test_resume_upload_graceful_handling(self):
        """
        Verify that corrupted / empty file upload does not raise an unhandled 500 error.
        """
        response = self.client.post(
            "/resume/upload",
            files={"file": ("corrupted.pdf", b"not-a-valid-pdf-stream", "application/pdf")}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["skills"], [])

    def test_backward_compatibility_endpoints(self):
        # 1. /matching/check
        res1 = self.client.post(
            "/matching/check",
            json={"student_skills": ["python"], "required_skills": ["python", "fastapi"]}
        )
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["match_percentage"], 50.0)

        # 2. /matching/semantic-match
        res2 = self.client.post(
            "/matching/semantic-match",
            json={"student_skills": ["python"], "required_skills": ["python"]}
        )
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["exact_matches"], ["python"])


if __name__ == "__main__":
    unittest.main()
