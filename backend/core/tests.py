"""
Django Automated Test Suite (Phase 8 Testing & Verification)
Run via: `python manage.py test`
Covers:
1. User registration, password hashing, login, and profile persistence.
2. PDF and DOCX resume upload, skill extraction, and AI resume analysis.
3. Interview configuration and dynamic resume-grounded question generation.
4. Contextual follow-up generation, 7-metric semantic answer evaluation, and grammar correction.
5. Adaptive difficulty progression and duplicate answer submission protection.
6. Recruiter job creation, multi-resume candidate screening, and fairness compliance.
"""
import json
from pathlib import Path
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import (
    CandidateProfile,
    Resume,
    InterviewSession,
    InterviewQuestion,
    InterviewResponse,
    ScreeningJob,
    CandidateScreening,
)


class AIInterviewerPlatformTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="arjun_test",
            email="arjun@test.edu",
            password="StrongPassword123!",
        )
        self.profile = CandidateProfile.objects.create(
            user=self.user,
            role="candidate",
            full_name="Arjun Sharma",
            preferred_domain="Machine Learning",
            skills_json=json.dumps(["Python", "Machine Learning", "Random Forest", "Flask"]),
        )
        self.client.login(username="arjun_test", password="StrongPassword123!")

    def test_01_dashboard_and_profile_access(self):
        resp = self.client.get("/dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Arjun Sharma")

    def test_02_resume_upload_and_skill_extraction(self):
        sample_pdf = Path(__file__).resolve().parent.parent.parent / "sample_data" / "Arjun_Sharma_ML_Resume.pdf"
        with open(sample_pdf, "rb") as fp:
            resp = self.client.post("/resume/", {
                "target_domain": "Machine Learning",
                "resume_file": fp,
            })
        self.assertEqual(resp.status_code, 302)
        resume = Resume.objects.filter(user=self.user).first()
        self.assertIsNotNone(resume)
        self.assertIn("Random Forest", resume.get_extracted_skills())

    def test_03_live_interview_flow_and_adaptive_evaluation(self):
        resp = self.client.post("/interview/configure/", {
            "domain": "Machine Learning",
            "interview_type": "Resume-Based Interview",
            "difficulty": "Adaptive",
            "duration_minutes": "15",
            "max_questions": "3",
            "selected_skills": "Python, Machine Learning, Random Forest, Flask",
        })
        self.assertEqual(resp.status_code, 302)
        session = InterviewSession.objects.filter(user=self.user).first()
        self.assertIsNotNone(session)
        first_q = session.questions.first()
        self.assertIsNotNone(first_q)

        # Submit answer via JSON API
        ans_resp = self.client.post(
            f"/interview/{session.id}/submit-answer/",
            data=json.dumps({
                "question_id": first_q.id,
                "answer_text": "Random Forest is an ensemble learning method that uses bootstrap aggregating and random feature selection across decision trees to reduce variance and prevent overfitting.",
                "input_type": "voice",
            }),
            content_type="application/json",
        )
        self.assertEqual(ans_resp.status_code, 200)
        payload = ans_resp.json()
        self.assertEqual(payload["status"], "next_question_ready")
        self.assertGreaterEqual(payload["evaluation"]["overall_score"], 7.5)

        # Verify duplicate submission prevention
        dup_resp = self.client.post(
            f"/interview/{session.id}/submit-answer/",
            data=json.dumps({
                "question_id": first_q.id,
                "answer_text": "Duplicate submission attempt",
                "input_type": "text",
            }),
            content_type="application/json",
        )
        self.assertEqual(dup_resp.status_code, 400)
