"""
Database Architecture (Module 14)
Implements all required models using Django ORM and SQLite:
1. User (Django built-in auth.models.User + role/metadata in CandidateProfile)
2. CandidateProfile
3. Resume
4. InterviewSession
5. InterviewQuestion
6. InterviewResponse
7. ScreeningJob
8. CandidateScreening
"""
import json
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


INTERVIEW_DOMAINS = [
    ("Python Development", "Python Development"),
    ("Java Development", "Java Development"),
    ("C/C++ Programming", "C/C++ Programming"),
    ("Data Structures and Algorithms", "Data Structures and Algorithms"),
    ("SQL and DBMS", "SQL and DBMS"),
    ("Data Analytics", "Data Analytics"),
    ("Data Science", "Data Science"),
    ("Machine Learning", "Machine Learning"),
    ("Artificial Intelligence", "Artificial Intelligence"),
    ("Generative AI", "Generative AI"),
    ("Natural Language Processing", "Natural Language Processing"),
    ("Deep Learning", "Deep Learning"),
    ("Web Development", "Web Development"),
    ("Frontend Development", "Frontend Development"),
    ("Backend Development", "Backend Development"),
    ("Full Stack Development", "Full Stack Development"),
    ("Software Engineering", "Software Engineering"),
    ("Operating Systems", "Operating Systems"),
    ("Computer Networks", "Computer Networks"),
    ("Cloud Computing", "Cloud Computing"),
    ("DevOps", "DevOps"),
    ("Cybersecurity", "Cybersecurity"),
    ("HR Interview", "HR Interview"),
    ("Behavioral Interview", "Behavioral Interview"),
]

DIFFICULTY_CHOICES = [
    ("Beginner", "Beginner"),
    ("Intermediate", "Intermediate"),
    ("Advanced", "Advanced"),
    ("Expert", "Expert"),
    ("Adaptive", "Adaptive"),
]

INTERVIEW_TYPE_CHOICES = [
    ("Technical Interview", "Technical Interview"),
    ("HR Interview", "HR Interview"),
    ("Behavioral Interview", "Behavioral Interview"),
    ("Resume-Based Interview", "Resume-Based Interview"),
    ("Project-Based Interview", "Project-Based Interview"),
    ("Mixed Interview", "Mixed Interview"),
]


class CandidateProfile(models.Model):
    ROLE_CHOICES = [
        ("candidate", "Candidate"),
        ("recruiter", "Recruiter"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="candidate")
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=30, blank=True, default="")
    education = models.CharField(max_length=255, blank=True, default="B.Tech in Computer Science and Engineering")
    graduation_year = models.IntegerField(default=2027)
    preferred_domain = models.CharField(max_length=100, choices=INTERVIEW_DOMAINS, default="Python Development")
    experience_level = models.CharField(max_length=80, default="Fresher / Final-Year Student")
    skills_json = models.TextField(default="[]", help_text="JSON array of technical skills")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_skills(self):
        try:
            data = json.loads(self.skills_json)
            return data if isinstance(data, list) else []
        except Exception:
            return [s.strip() for s in self.skills_json.split(",") if s.strip()]

    def set_skills(self, skill_list):
        if isinstance(skill_list, str):
            skill_list = [s.strip() for s in skill_list.split(",") if s.strip()]
        self.skills_json = json.dumps(list(dict.fromkeys(skill_list)))

    def __str__(self):
        return f"{self.full_name or self.user.username} ({self.role})"


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resumes")
    file = models.FileField(upload_to="resumes/", blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, default="")
    original_filename = models.CharField(max_length=255)
    extracted_text = models.TextField(blank=True, default="")
    extracted_skills_json = models.TextField(default="[]")
    extracted_metadata_json = models.TextField(default="{}")
    analysis_report_json = models.TextField(default="{}")
    extraction_status = models.CharField(max_length=50, default="Completed")
    is_active = models.BooleanField(default=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-upload_date"]

    def get_extracted_skills(self):
        try:
            return json.loads(self.extracted_skills_json)
        except Exception:
            return []

    def get_extracted_metadata(self):
        try:
            return json.loads(self.extracted_metadata_json)
        except Exception:
            return {}

    def get_analysis_report(self):
        try:
            return json.loads(self.analysis_report_json)
        except Exception:
            return {}

    def __str__(self):
        return f"Resume #{self.id} - {self.original_filename} ({self.user.username})"


class InterviewSession(models.Model):
    STATUS_CHOICES = [
        ("configured", "Configured"),
        ("in_progress", "In Progress"),
        ("paused", "Paused"),
        ("completed", "Completed"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="interview_sessions")
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True, related_name="sessions")
    domain = models.CharField(max_length=100, choices=INTERVIEW_DOMAINS, default="Python Development")
    subtopics_json = models.TextField(default="[]")
    selected_skills_json = models.TextField(default="[]")
    interview_type = models.CharField(max_length=80, choices=INTERVIEW_TYPE_CHOICES, default="Technical Interview")
    difficulty = models.CharField(max_length=40, choices=DIFFICULTY_CHOICES, default="Intermediate")
    current_difficulty = models.CharField(max_length=40, default="Intermediate")
    adaptive_enabled = models.BooleanField(default=True)
    duration_minutes = models.IntegerField(default=15)
    max_questions = models.IntegerField(default=10)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="in_progress")
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    overall_score = models.FloatField(default=0.0)
    final_report_json = models.TextField(default="{}")

    class Meta:
        ordering = ["-start_time"]

    def get_selected_skills(self):
        try:
            return json.loads(self.selected_skills_json)
        except Exception:
            return []

    def get_subtopics(self):
        try:
            return json.loads(self.subtopics_json)
        except Exception:
            return []

    def get_final_report(self):
        try:
            return json.loads(self.final_report_json)
        except Exception:
            return {}

    def __str__(self):
        return f"Session #{self.id} - {self.user.username} - {self.domain} ({self.status})"


class InterviewQuestion(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    question_category = models.CharField(max_length=80, default="Conceptual")
    topic = models.CharField(max_length=150, default="")
    difficulty = models.CharField(max_length=40, default="Intermediate")
    sequence_number = models.IntegerField(default=1)
    is_followup = models.BooleanField(default=False)
    follow_up_rationale = models.TextField(blank=True, default="")
    expected_concepts_json = models.TextField(default="[]")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sequence_number"]

    def get_expected_concepts(self):
        try:
            return json.loads(self.expected_concepts_json)
        except Exception:
            return []

    def __str__(self):
        return f"Q{self.sequence_number} (Session #{self.session_id}): {self.question_text[:60]}"


class InterviewResponse(models.Model):
    INPUT_TYPE_CHOICES = [
        ("text", "Text Input"),
        ("voice", "Microphone Speech-to-Text"),
        ("skipped", "Skipped Question"),
    ]
    question = models.OneToOneField(InterviewQuestion, on_delete=models.CASCADE, related_name="response")
    answer_text = models.TextField(blank=True, default="")
    corrected_answer_text = models.TextField(blank=True, default="")
    input_type = models.CharField(max_length=20, choices=INPUT_TYPE_CHOICES, default="text")
    evaluation_data_json = models.TextField(default="{}")
    score = models.FloatField(default=0.0)
    technical_score = models.FloatField(default=0.0)
    conceptual_score = models.FloatField(default=0.0)
    relevance_score = models.FloatField(default=0.0)
    completeness_score = models.FloatField(default=0.0)
    communication_score = models.FloatField(default=0.0)
    grammar_score = models.FloatField(default=0.0)
    feedback = models.TextField(blank=True, default="")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def get_evaluation_data(self):
        try:
            return json.loads(self.evaluation_data_json)
        except Exception:
            return {}

    def __str__(self):
        return f"Response to Q#{self.question_id} - Score: {self.score}/10"


class ScreeningJob(models.Model):
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="screening_jobs")
    job_title = models.CharField(max_length=200)
    job_description = models.TextField()
    required_skills_json = models.TextField(default="[]")
    preferred_qualifications_json = models.TextField(default="[]")
    minimum_experience_years = models.FloatField(default=0.0)
    educational_requirements = models.CharField(max_length=255, default="B.Tech / B.E. in Computer Science or equivalent")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def get_required_skills(self):
        try:
            return json.loads(self.required_skills_json)
        except Exception:
            return []

    def get_preferred_qualifications(self):
        try:
            return json.loads(self.preferred_qualifications_json)
        except Exception:
            return []

    def __str__(self):
        return f"{self.job_title} (by {self.recruiter.username})"


class CandidateScreening(models.Model):
    job = models.ForeignKey(ScreeningJob, on_delete=models.CASCADE, related_name="screenings")
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="screenings")
    candidate_name = models.CharField(max_length=150, default="Candidate")
    match_score = models.FloatField(default=0.0)
    screening_report_json = models.TextField(default="{}")
    screened_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-match_score", "-screened_at"]

    def get_screening_report(self):
        try:
            return json.loads(self.screening_report_json)
        except Exception:
            return {}

    def __str__(self):
        return f"{self.candidate_name} -> {self.job.job_title} ({self.match_score}%)"
