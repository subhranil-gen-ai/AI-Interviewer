# Generated initial migration for AI Interviewer Platform (Module 14)
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CandidateProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("candidate", "Candidate"), ("recruiter", "Recruiter")], default="candidate", max_length=20)),
                ("full_name", models.CharField(max_length=150)),
                ("phone_number", models.CharField(blank=True, default="", max_length=30)),
                ("education", models.CharField(blank=True, default="B.Tech in Computer Science and Engineering", max_length=255)),
                ("graduation_year", models.IntegerField(default=2027)),
                ("preferred_domain", models.CharField(default="Python Development", max_length=100)),
                ("experience_level", models.CharField(default="Fresher / Final-Year Student", max_length=80)),
                ("skills_json", models.TextField(default="[]")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Resume",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(blank=True, null=True, upload_to="resumes/")),
                ("file_path", models.CharField(blank=True, default="", max_length=500)),
                ("original_filename", models.CharField(max_length=255)),
                ("extracted_text", models.TextField(blank=True, default="")),
                ("extracted_skills_json", models.TextField(default="[]")),
                ("extracted_metadata_json", models.TextField(default="{}")),
                ("analysis_report_json", models.TextField(default="{}")),
                ("extraction_status", models.CharField(default="Completed", max_length=50)),
                ("is_active", models.BooleanField(default=True)),
                ("upload_date", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="resumes", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-upload_date"]},
        ),
        migrations.CreateModel(
            name="InterviewSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("domain", models.CharField(default="Python Development", max_length=100)),
                ("subtopics_json", models.TextField(default="[]")),
                ("selected_skills_json", models.TextField(default="[]")),
                ("interview_type", models.CharField(default="Technical Interview", max_length=80)),
                ("difficulty", models.CharField(default="Intermediate", max_length=40)),
                ("current_difficulty", models.CharField(default="Intermediate", max_length=40)),
                ("adaptive_enabled", models.BooleanField(default=True)),
                ("duration_minutes", models.IntegerField(default=15)),
                ("max_questions", models.IntegerField(default=6)),
                ("status", models.CharField(default="in_progress", max_length=30)),
                ("start_time", models.DateTimeField(default=django.utils.timezone.now)),
                ("end_time", models.DateTimeField(blank=True, null=True)),
                ("overall_score", models.FloatField(default=0.0)),
                ("final_report_json", models.TextField(default="{}")),
                ("resume", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="sessions", to="core.resume")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="interview_sessions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-start_time"]},
        ),
        migrations.CreateModel(
            name="InterviewQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question_text", models.TextField()),
                ("question_category", models.CharField(default="Conceptual", max_length=80)),
                ("topic", models.CharField(default="", max_length=150)),
                ("difficulty", models.CharField(default="Intermediate", max_length=40)),
                ("sequence_number", models.IntegerField(default=1)),
                ("is_followup", models.BooleanField(default=False)),
                ("follow_up_rationale", models.TextField(blank=True, default="")),
                ("expected_concepts_json", models.TextField(default="[]")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="core.interviewsession")),
            ],
            options={"ordering": ["sequence_number"]},
        ),
        migrations.CreateModel(
            name="InterviewResponse",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("answer_text", models.TextField(blank=True, default="")),
                ("corrected_answer_text", models.TextField(blank=True, default="")),
                ("input_type", models.CharField(default="text", max_length=20)),
                ("evaluation_data_json", models.TextField(default="{}")),
                ("score", models.FloatField(default=0.0)),
                ("technical_score", models.FloatField(default=0.0)),
                ("conceptual_score", models.FloatField(default=0.0)),
                ("relevance_score", models.FloatField(default=0.0)),
                ("completeness_score", models.FloatField(default=0.0)),
                ("communication_score", models.FloatField(default=0.0)),
                ("grammar_score", models.FloatField(default=0.0)),
                ("feedback", models.TextField(blank=True, default="")),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("question", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="response", to="core.interviewquestion")),
            ],
        ),
        migrations.CreateModel(
            name="ScreeningJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("job_title", models.CharField(max_length=200)),
                ("job_description", models.TextField()),
                ("required_skills_json", models.TextField(default="[]")),
                ("preferred_qualifications_json", models.TextField(default="[]")),
                ("minimum_experience_years", models.FloatField(default=0.0)),
                ("educational_requirements", models.CharField(default="B.Tech / B.E. in Computer Science or equivalent", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("recruiter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="screening_jobs", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="CandidateScreening",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("candidate_name", models.CharField(default="Candidate", max_length=150)),
                ("match_score", models.FloatField(default=0.0)),
                ("screening_report_json", models.TextField(default="{}")),
                ("screened_at", models.DateTimeField(auto_now_add=True)),
                ("job", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="screenings", to="core.screeningjob")),
                ("resume", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="screenings", to="core.resume")),
            ],
            options={"ordering": ["-match_score", "-screened_at"]},
        ),
    ]
