from django.urls import path
from . import views

urlpatterns = [
    # Public & Authentication (Module 1)
    path("", views.landing_page, name="landing"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Candidate Dashboard & Profile (Modules 1 & 2)
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),

    # Resume Upload & AI Analysis (Module 3)
    path("resume/", views.resume_upload_view, name="resume_upload"),
    path("resume/<int:resume_id>/analysis/", views.resume_analysis_view, name="resume_analysis"),
    path("resume/<int:resume_id>/update-skills/", views.resume_update_skills_view, name="resume_update_skills"),
    path("resume/<int:resume_id>/delete/", views.resume_delete_view, name="resume_delete"),

    # Interview Configuration & Live AI Interview Room (Modules 4, 5, 6, 7, 8, 9)
    path("interview/configure/", views.interview_configure_view, name="interview_configure"),
    path("interview/<int:session_id>/room/", views.live_interview_room_view, name="live_interview_room"),
    path("interview/<int:session_id>/submit-answer/", views.submit_answer_api, name="submit_answer_api"),
    path("interview/<int:session_id>/skip-question/", views.skip_question_api, name="skip_question_api"),
    path("interview/<int:session_id>/toggle-pause/", views.toggle_pause_api, name="toggle_pause_api"),
    path("interview/<int:session_id>/end/", views.end_interview_view, name="end_interview"),

    # Interview Reports, History & Performance Analytics (Modules 11 & 12)
    path("interview/<int:session_id>/result/", views.interview_result_view, name="interview_result"),
    path("history/", views.interview_history_view, name="interview_history"),
    path("analytics/", views.performance_analytics_view, name="performance_analytics"),

    # Recruiter Candidate Screening & Comparison System (Module 10)
    path("recruiter/", views.recruiter_dashboard_view, name="recruiter_dashboard"),
    path("recruiter/jobs/create/", views.job_create_view, name="job_create"),
    path("recruiter/jobs/<int:job_id>/screen/", views.candidate_screening_view, name="candidate_screening"),
    path("recruiter/jobs/<int:job_id>/compare/", views.candidate_comparison_view, name="candidate_comparison"),
]
