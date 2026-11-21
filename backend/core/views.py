"""
Django Views & Controllers for AI Interviewer Platform (All 12 Modules & 16 Required Pages).
Enforces authentication, CSRF protection, file upload validation, duplicate submission prevention,
and user-isolated data access controls (Module 17).
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Avg, Max

from .models import (
    CandidateProfile,
    Resume,
    InterviewSession,
    InterviewQuestion,
    InterviewResponse,
    ScreeningJob,
    CandidateScreening,
    INTERVIEW_DOMAINS,
    DIFFICULTY_CHOICES,
    INTERVIEW_TYPE_CHOICES,
)
from .services import (
    call_fastapi_extract_resume,
    call_fastapi_analyze_resume,
    call_fastapi_generate_question,
    call_fastapi_evaluate_answer,
    call_fastapi_adaptive_difficulty,
    call_fastapi_screen_candidate,
    call_fastapi_final_report,
)


DOMAIN_SUBTOPICS_MAP = {
    "Python Development": ["Decorators & Closures", "Generators & Asyncio", "Memory Management & GIL", "OOP & Metaclasses", "Testing & Packaging"],
    "Java Development": ["JVM Internals & GC", "Multithreading & Concurrency", "Collections Framework", "Spring Boot Architecture", "Streams & Lambdas"],
    "C/C++ Programming": ["Pointers & Memory Layout", "RAII & Smart Pointers", "STL Containers", "Virtual Functions & VTable", "Multithreading"],
    "Data Structures and Algorithms": ["Arrays & Hash Maps", "Trees & Graphs (BFS/DFS)", "Dynamic Programming", "Heaps & Priority Queues", "Sorting & Searching"],
    "SQL and DBMS": ["B+ Tree Indexing", "ACID & MVCC Transactions", "Normalization (1NF-BCNF)", "Complex Joins & Window Functions", "Query Execution Plans"],
    "Data Analytics": ["Exploratory Data Analysis", "Statistical Hypothesis Testing", "SQL Aggregation", "KPI Dashboard Design", "Data Cleaning"],
    "Data Science": ["Feature Engineering", "Probability & Statistics", "A/B Experimentation", "Time-Series Forecasting", "Model Explainability"],
    "Machine Learning": ["Ensemble Models (Random Forest/XGBoost)", "Overfitting & Regularization", "Imbalanced Data & SMOTE", "Evaluation Metrics (PR-AUC/F1)", "Model Deployment (Flask/FastAPI)"],
    "Artificial Intelligence": ["Search Algorithms (A* / Minimax)", "Knowledge Representation", "Agentic Architectures", "Reinforcement Learning", "AI Ethics & Safety"],
    "Generative AI": ["Large Language Models (LLMs)", "Prompt Engineering & JSON Schemas", "RAG Pipelines & Vector DBs", "Fine-Tuning (LoRA/QLoRA)", "Hallucination Mitigation"],
    "Natural Language Processing": ["Tokenization & Lemmatization", "TF-IDF & Cosine Similarity", "Transformer Self-Attention", "Named Entity Recognition", "Sentiment & Semantic Evaluation"],
    "Deep Learning": ["Backpropagation & Optimizers", "CNNs & Computer Vision", "RNNs/LSTMs vs Transformers", "Batch Norm & Dropout", "Transfer Learning"],
    "Web Development": ["HTTP/HTTPS & REST Principles", "Authentication (JWT/Session)", "CORS & CSRF Security", "Browser Rendering Pipeline", "Caching Strategies"],
    "Frontend Development": ["DOM Manipulation & Events", "Responsive CSS Grid/Flexbox", "Web Speech & Media APIs", "State Management", "Web Accessibility (WCAG)"],
    "Backend Development": ["Django ORM & Middleware", "FastAPI Async Microservices", "Database Indexing & Scaling", "Rate Limiting & Security", "Background Task Queues"],
    "Full Stack Development": ["End-to-End API Integration", "Database Schema Design", "Authentication & Role Access", "Frontend-Backend State Sync", "Cloud Deployment"],
    "Software Engineering": ["SOLID Principles & Design Patterns", "Microservices vs Monolith", "CI/CD & Automated Testing", "Agile & Code Review", "System Maintainability"],
    "Operating Systems": ["Process vs Thread Scheduling", "Deadlocks & Banker's Algorithm", "Virtual Memory & Paging", "Semaphores & Mutexes", "File Systems & Disk I/O"],
    "Computer Networks": ["OSI & TCP/IP Stack", "TCP Handshake & Congestion Control", "DNS & HTTP/2/3", "TLS/SSL Encryption", "Routing Protocols"],
    "Cloud Computing": ["IAM & VPC Networking", "Serverless vs Containers", "Auto-Scaling & Load Balancing", "Object Storage & CDNs", "Cloud Cost Optimization"],
    "DevOps": ["Docker Containerization", "Kubernetes Orchestration", "GitHub Actions CI/CD", "Infrastructure as Code", "Monitoring & Logging"],
    "Cybersecurity": ["OWASP Top 10 Vulnerabilities", "SQL Injection & XSS Prevention", "Password Hashing (PBKDF2/Argon2)", "Zero-Trust Access Control", "API Key Security"],
    "HR Interview": ["Career Goals & Motivation", "Strengths & Growth Areas", "Team Collaboration", "Adaptability Under Deadlines", "Company Culture Alignment"],
    "Behavioral Interview": ["STAR Method Problem Solving", "Conflict Resolution", "Leadership & Ownership", "Handling Project Failure", "Prioritization Under Pressure"],
}


def _ensure_profile(user: User) -> CandidateProfile:
    profile, _ = CandidateProfile.objects.get_or_create(
        user=user,
        defaults={
            "full_name": user.get_full_name() or user.username,
            "skills_json": json.dumps(["Python", "Machine Learning", "Django", "FastAPI", "SQL"]),
        },
    )
    return profile


# =============================================================================
# PAGE 1: Landing Page
# =============================================================================
def landing_page(request):
    return render(request, "core/landing.html", {
        "domains_count": len(INTERVIEW_DOMAINS),
    })


# =============================================================================
# PAGE 2 & 3: Registration, Login, Logout (Module 1)
# =============================================================================
def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        role = request.POST.get("role", "candidate").strip()
        phone = request.POST.get("phone_number", "").strip()
        education = request.POST.get("education", "B.Tech in Computer Science and Engineering").strip()
        grad_year = int(request.POST.get("graduation_year", 2027) or 2027)
        preferred_domain = request.POST.get("preferred_domain", "Python Development")
        experience_level = request.POST.get("experience_level", "Fresher / Final-Year Student")
        raw_skills = request.POST.get("skills", "Python, SQL, Data Structures, Machine Learning")

        if not username or not email or not password:
            messages.error(request, "Username, email, and password are required.")
            return render(request, "core/register.html", {"domains": INTERVIEW_DOMAINS})

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "core/register.html", {"domains": INTERVIEW_DOMAINS})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken. Please choose another.")
            return render(request, "core/register.html", {"domains": INTERVIEW_DOMAINS})

        try:
            validate_password(password)
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))
            return render(request, "core/register.html", {"domains": INTERVIEW_DOMAINS})

        user = User.objects.create_user(username=username, email=email, password=password)
        names = full_name.split(" ", 1)
        user.first_name = names[0]
        if len(names) > 1:
            user.last_name = names[1]
        user.save()

        profile = CandidateProfile.objects.create(
            user=user,
            role=role if role in ("candidate", "recruiter") else "candidate",
            full_name=full_name or username,
            phone_number=phone,
            education=education,
            graduation_year=grad_year,
            preferred_domain=preferred_domain,
            experience_level=experience_level,
        )
        profile.set_skills(raw_skills)
        profile.save()

        login(request, user)
        messages.success(request, f"Welcome to AI Interviewer, {profile.full_name}!")
        if profile.role == "recruiter":
            return redirect("recruiter_dashboard")
        return redirect("dashboard")

    return render(request, "core/register.html", {"domains": INTERVIEW_DOMAINS})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            profile = _ensure_profile(user)
            messages.success(request, f"Welcome back, {profile.full_name}!")
            if profile.role == "recruiter":
                return redirect("recruiter_dashboard")
            return redirect("dashboard")
        messages.error(request, "Invalid username or password.")

    return render(request, "core/login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been securely logged out.")
    return redirect("landing")


# =============================================================================
# PAGE 4: Candidate Dashboard (Module 2)
# =============================================================================
@login_required
def dashboard_view(request):
    profile = _ensure_profile(request.user)
    completed_sessions = InterviewSession.objects.filter(user=request.user, status="completed")
    total_completed = completed_sessions.count()
    agg = completed_sessions.aggregate(avg_score=Avg("overall_score"), max_score=Max("overall_score"))
    avg_score = round(agg["avg_score"] or 0.0, 2)
    max_score = round(agg["max_score"] or 0.0, 2)

    recent_sessions = InterviewSession.objects.filter(user=request.user).order_by("-start_time")[:6]
    active_resume = Resume.objects.filter(user=request.user, is_active=True).first()

    # Compute strongest & weakest technical skills from actual database responses
    strongest_skills = []
    weakest_skills = []
    if active_resume:
        analysis = active_resume.get_analysis_report()
        strongest_skills = analysis.get("strong_technical_areas", [])[:3]
        weakest_skills = analysis.get("weak_or_missing_areas", [])[:3]
    if not strongest_skills:
        strongest_skills = profile.get_skills()[:3] or ["Python", "Problem Solving"]
    if not weakest_skills:
        weakest_skills = ["System Scalability Metrics", "Production Edge-Case Testing"]

    # Chart.js real session trend data
    chronological = list(completed_sessions.order_by("start_time")[:10])
    chart_labels = [f"#{s.id} {s.domain[:12]}" for s in chronological]
    chart_scores = [round(s.overall_score, 2) for s in chronological]

    return render(request, "core/dashboard.html", {
        "profile": profile,
        "total_completed": total_completed,
        "avg_score": avg_score,
        "max_score": max_score,
        "recent_sessions": recent_sessions,
        "active_resume": active_resume,
        "strongest_skills": strongest_skills,
        "weakest_skills": weakest_skills,
        "chart_labels_json": json.dumps(chart_labels),
        "chart_scores_json": json.dumps(chart_scores),
    })


# =============================================================================
# PAGE 5: User Profile & Editing (Module 1)
# =============================================================================
@login_required
def profile_view(request):
    profile = _ensure_profile(request.user)
    if request.method == "POST":
        profile.full_name = request.POST.get("full_name", profile.full_name).strip()
        request.user.email = request.POST.get("email", request.user.email).strip()
        request.user.save()
        profile.phone_number = request.POST.get("phone_number", "").strip()
        profile.education = request.POST.get("education", "").strip()
        profile.graduation_year = int(request.POST.get("graduation_year", 2027) or 2027)
        profile.preferred_domain = request.POST.get("preferred_domain", profile.preferred_domain)
        profile.experience_level = request.POST.get("experience_level", profile.experience_level).strip()
        profile.role = request.POST.get("role", profile.role)
        profile.set_skills(request.POST.get("skills", ""))
        profile.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("profile")

    return render(request, "core/profile.html", {
        "profile": profile,
        "domains": INTERVIEW_DOMAINS,
        "skills_csv": ", ".join(profile.get_skills()),
    })


# =============================================================================
# PAGE 6 & 7: Resume Upload & AI Resume Analysis (Module 3)
# =============================================================================
@login_required
def resume_upload_view(request):
    profile = _ensure_profile(request.user)
    resumes = Resume.objects.filter(user=request.user)
    active_resume = resumes.filter(is_active=True).first()

    if request.method == "POST":
        uploaded_file = request.FILES.get("resume_file")
        pasted_text = request.POST.get("pasted_resume_text", "").strip()
        target_domain = request.POST.get("target_domain", profile.preferred_domain)

        try:
            if uploaded_file:
                fname = uploaded_file.name
                fbytes = uploaded_file.read()
                extracted = call_fastapi_extract_resume(fbytes, fname)
            elif pasted_text:
                fname = "pasted_resume.txt"
                fbytes = pasted_text.encode("utf-8")
                extracted = call_fastapi_extract_resume(fbytes, fname)
            else:
                messages.error(request, "Please select a PDF/DOCX file to upload or paste your resume text.")
                return redirect("resume_upload")

            raw_text = extracted.get("raw_text", "")
            analysis = call_fastapi_analyze_resume(
                resume_text=raw_text,
                extracted_data=extracted,
                target_domain=target_domain,
            )

            # Deactivate older resumes
            Resume.objects.filter(user=request.user).update(is_active=False)

            new_resume = Resume.objects.create(
                user=request.user,
                file=uploaded_file if uploaded_file else None,
                original_filename=fname,
                extracted_text=raw_text,
                extracted_skills_json=json.dumps(extracted.get("technical_skills", [])),
                extracted_metadata_json=json.dumps(extracted),
                analysis_report_json=json.dumps(analysis),
                extraction_status="Verified & Analyzed",
                is_active=True,
            )

            # Sync extracted skills into candidate profile
            merged_skills = list(dict.fromkeys(extracted.get("technical_skills", []) + profile.get_skills()))
            profile.set_skills(merged_skills)
            profile.save()

            messages.success(request, f"Resume '{fname}' uploaded, parsed, and analyzed by AI.")
            return redirect("resume_analysis", resume_id=new_resume.id)

        except ValueError as exc:
            messages.error(request, str(exc))
        except Exception as exc:
            messages.error(request, f"Error processing resume: {exc}")

    return render(request, "core/resume_upload.html", {
        "profile": profile,
        "resumes": resumes,
        "active_resume": active_resume,
        "domains": INTERVIEW_DOMAINS,
    })


@login_required
def resume_analysis_view(request, resume_id: int):
    resume = get_object_or_404(Resume, id=resume_id)
    if resume.user != request.user and _ensure_profile(request.user).role != "recruiter":
        return HttpResponseForbidden("Access denied: You cannot view another candidate's private resume.")

    metadata = resume.get_extracted_metadata()
    analysis = resume.get_analysis_report()
    skills = resume.get_extracted_skills()

    return render(request, "core/resume_analysis.html", {
        "resume": resume,
        "metadata": metadata,
        "analysis": analysis,
        "skills": skills,
        "skills_csv": ", ".join(skills),
    })


@login_required
@require_POST
def resume_update_skills_view(request, resume_id: int):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    updated_csv = request.POST.get("skills_csv", "")
    skill_list = list(dict.fromkeys([s.strip() for s in updated_csv.split(",") if s.strip()]))
    resume.extracted_skills_json = json.dumps(skill_list)
    meta = resume.get_extracted_metadata()
    meta["technical_skills"] = skill_list
    resume.extracted_metadata_json = json.dumps(meta)
    resume.save()

    profile = _ensure_profile(request.user)
    profile.set_skills(skill_list)
    profile.save()

    messages.success(request, f"Updated and verified {len(skill_list)} skills for interview generation.")
    return redirect("resume_analysis", resume_id=resume.id)


@login_required
@require_POST
def resume_delete_view(request, resume_id: int):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    fname = resume.original_filename
    resume.delete()
    latest = Resume.objects.filter(user=request.user).first()
    if latest:
        latest.is_active = True
        latest.save()
    messages.info(request, f"Removed resume '{fname}'.")
    return redirect("resume_upload")


# =============================================================================
# PAGE 8: Interview Configuration (Module 4)
# =============================================================================
@login_required
def interview_configure_view(request):
    profile = _ensure_profile(request.user)
    active_resume = Resume.objects.filter(user=request.user, is_active=True).first()
    resume_skills = active_resume.get_extracted_skills() if active_resume else []
    combined_skills = list(dict.fromkeys(resume_skills + profile.get_skills()))

    if request.method == "POST":
        domain = request.POST.get("domain", profile.preferred_domain)
        subtopics_raw = request.POST.getlist("subtopics")
        custom_subtopics = [s.strip() for s in request.POST.get("custom_subtopics", "").split(",") if s.strip()]
        subtopics = list(dict.fromkeys(subtopics_raw + custom_subtopics))

        skills_csv = request.POST.get("selected_skills", "")
        selected_skills = list(dict.fromkeys([s.strip() for s in skills_csv.split(",") if s.strip()]))
        if not selected_skills:
            selected_skills = combined_skills or [domain]

        difficulty_choice = request.POST.get("difficulty", "Adaptive")
        adaptive_enabled = (difficulty_choice == "Adaptive") or (request.POST.get("enable_adaptive") == "on")
        initial_difficulty = "Intermediate" if difficulty_choice == "Adaptive" else difficulty_choice

        interview_type = request.POST.get("interview_type", "Technical Interview")
        duration_choice = request.POST.get("duration_minutes", "15")
        if duration_choice == "custom":
            duration_minutes = max(5, min(120, int(request.POST.get("custom_duration", 20) or 20)))
        else:
            duration_minutes = int(duration_choice or 15)

        max_questions = max(1, min(50, int(request.POST.get("max_questions", 6) or 6)))

        session = InterviewSession.objects.create(
            user=request.user,
            resume=active_resume,
            domain=domain,
            subtopics_json=json.dumps(subtopics),
            selected_skills_json=json.dumps(selected_skills),
            interview_type=interview_type,
            difficulty=difficulty_choice,
            current_difficulty=initial_difficulty,
            adaptive_enabled=adaptive_enabled,
            duration_minutes=duration_minutes,
            max_questions=max_questions,
            status="in_progress",
        )

        # Generate the opening interview question immediately via FastAPI AI service
        resume_text = active_resume.extracted_text if active_resume else ""
        projects = active_resume.get_extracted_metadata().get("projects", []) if active_resume else []
        q_data = call_fastapi_generate_question({
            "domain": domain,
            "subtopics": subtopics,
            "skills": selected_skills,
            "interview_type": interview_type,
            "difficulty": initial_difficulty,
            "resume_text": resume_text,
            "projects": projects,
            "previous_questions": [],
            "conversation_history": [],
            "question_number": 1,
            "max_questions": max_questions,
            "duration_minutes": duration_minutes,
        })

        InterviewQuestion.objects.create(
            session=session,
            question_text=q_data.get("question_text", f"Welcome! Let's begin our {domain} interview."),
            question_category=q_data.get("question_category", "Conceptual"),
            topic=q_data.get("topic", domain),
            difficulty=q_data.get("difficulty", initial_difficulty),
            sequence_number=1,
            is_followup=bool(q_data.get("is_followup", False)),
            follow_up_rationale=q_data.get("follow_up_rationale", ""),
            expected_concepts_json=json.dumps(q_data.get("expected_key_concepts", [])),
        )

        return redirect("live_interview_room", session_id=session.id)

    return render(request, "core/interview_configure.html", {
        "profile": profile,
        "active_resume": active_resume,
        "domains": INTERVIEW_DOMAINS,
        "difficulties": DIFFICULTY_CHOICES,
        "interview_types": INTERVIEW_TYPE_CHOICES,
        "combined_skills": combined_skills,
        "skills_csv": ", ".join(combined_skills),
        "subtopics_map_json": json.dumps(DOMAIN_SUBTOPICS_MAP),
    })


# =============================================================================
# PAGE 9: Live AI Interview Room & Conversational Engine (Modules 5, 6, 7, 8, 9)
# =============================================================================
@login_required
def live_interview_room_view(request, session_id: int):
    session = get_object_or_404(InterviewSession, id=session_id)
    if session.user != request.user:
        return HttpResponseForbidden("Access denied: This interview session belongs to another candidate.")

    if session.status == "completed":
        return redirect("interview_result", session_id=session.id)

    questions = list(session.questions.all().order_by("sequence_number"))
    current_question = None
    answered_history = []
    for q in questions:
        if hasattr(q, "response"):
            answered_history.append({
                "sequence": q.sequence_number,
                "question_text": q.question_text,
                "category": q.question_category,
                "difficulty": q.difficulty,
                "answer_text": q.response.answer_text,
                "corrected_answer": q.response.corrected_answer_text,
                "score": q.response.score,
                "feedback": q.response.feedback,
                "evaluation": q.response.get_evaluation_data(),
            })
        elif current_question is None:
            current_question = q

    if current_question is None:
        return redirect("end_interview", session_id=session.id)

    progress_pct = int(((current_question.sequence_number - 1) / max(1, session.max_questions)) * 100)

    return render(request, "core/live_interview_room.html", {
        "session": session,
        "current_question": current_question,
        "answered_history": answered_history,
        "progress_pct": progress_pct,
        "selected_skills": session.get_selected_skills(),
    })


@login_required
@require_POST
def submit_answer_api(request, session_id: int):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    if session.status == "completed":
        return JsonResponse({"status": "completed", "redirect_url": f"/interview/{session.id}/result/"})

    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else request.POST
    except Exception:
        body = request.POST

    question_id = int(body.get("question_id", 0) or 0)
    answer_text = (body.get("answer_text") or "").strip()
    input_type = body.get("input_type", "text")

    question = get_object_or_404(InterviewQuestion, id=question_id, session=session)

    # Duplicate submission prevention (Module 17)
    if hasattr(question, "response"):
        return JsonResponse({
            "error": "This question has already been answered.",
            "already_submitted": True,
        }, status=400)

    if not answer_text:
        return JsonResponse({"error": "Please enter or record an answer before submitting (or use Skip Question)."}, status=400)

    resume_text = session.resume.extracted_text if session.resume else ""

    # 1. Evaluate Answer & Grammar via FastAPI AI Service (Modules 7 & 8)
    eval_result = call_fastapi_evaluate_answer({
        "question_text": question.question_text,
        "question_category": question.question_category,
        "difficulty": question.difficulty,
        "domain": session.domain,
        "candidate_answer": answer_text,
        "expected_key_concepts": question.get_expected_concepts(),
        "resume_context": resume_text[:1500],
    })

    gram_data = eval_result.get("grammar_analysis", {})
    overall_q_score = float(eval_result.get("overall_score", 7.0))

    InterviewResponse.objects.create(
        question=question,
        answer_text=answer_text,
        corrected_answer_text=gram_data.get("corrected_answer", answer_text),
        input_type=input_type if input_type in ("text", "voice", "skipped") else "text",
        evaluation_data_json=json.dumps(eval_result),
        score=overall_q_score,
        technical_score=float(eval_result.get("technical_correctness", 0)),
        conceptual_score=float(eval_result.get("conceptual_understanding", 0)),
        relevance_score=float(eval_result.get("relevance", 0)),
        completeness_score=float(eval_result.get("completeness", 0)),
        communication_score=float(eval_result.get("communication_quality", 0)),
        grammar_score=float(eval_result.get("grammar", 0)),
        feedback=eval_result.get("overall_evaluation", ""),
    )

    # 2. Update running session score & compute Adaptive Difficulty (Module 9)
    all_responses = InterviewResponse.objects.filter(question__session=session).order_by("question__sequence_number")
    recent_scores = [r.score for r in all_responses]
    session.overall_score = round(sum(recent_scores) / max(1, len(recent_scores)), 2)

    adaptive_info = call_fastapi_adaptive_difficulty(
        current_difficulty=session.current_difficulty,
        recent_scores=recent_scores,
        adaptive_enabled=session.adaptive_enabled,
    )
    session.current_difficulty = adaptive_info.get("recommended_difficulty", session.current_difficulty)
    session.save()

    # 3. Check if we reached max_questions; if not, generate next contextual follow-up question
    next_seq = question.sequence_number + 1
    if next_seq > session.max_questions:
        _finalize_interview_session(session)
        return JsonResponse({
            "status": "interview_completed",
            "evaluation": eval_result,
            "adaptive": adaptive_info,
            "redirect_url": f"/interview/{session.id}/result/",
        })

    prev_questions = [q.question_text for q in session.questions.all()]
    conv_history = []
    for q in session.questions.all().order_by("sequence_number"):
        if hasattr(q, "response"):
            ev = q.response.get_evaluation_data()
            conv_history.append({
                "question": q.question_text,
                "topic": q.topic,
                "answer": q.response.answer_text,
                "score": q.response.score,
                "quality_tier": ev.get("answer_quality_tier", "strong"),
                "missing_concepts": ev.get("missing_concepts", []),
            })

    projects = session.resume.get_extracted_metadata().get("projects", []) if session.resume else []
    next_q_data = call_fastapi_generate_question({
        "domain": session.domain,
        "subtopics": session.get_subtopics(),
        "skills": session.get_selected_skills(),
        "interview_type": session.interview_type,
        "difficulty": session.current_difficulty,
        "resume_text": resume_text,
        "projects": projects,
        "previous_questions": prev_questions,
        "conversation_history": conv_history,
        "question_number": next_seq,
        "max_questions": session.max_questions,
        "duration_minutes": session.duration_minutes,
    })

    next_question = InterviewQuestion.objects.create(
        session=session,
        question_text=next_q_data.get("question_text", ""),
        question_category=next_q_data.get("question_category", "Conceptual"),
        topic=next_q_data.get("topic", session.domain),
        difficulty=next_q_data.get("difficulty", session.current_difficulty),
        sequence_number=next_seq,
        is_followup=bool(next_q_data.get("is_followup", True)),
        follow_up_rationale=next_q_data.get("follow_up_rationale", ""),
        expected_concepts_json=json.dumps(next_q_data.get("expected_key_concepts", [])),
    )

    return JsonResponse({
        "status": "next_question_ready",
        "evaluation": eval_result,
        "adaptive": adaptive_info,
        "session_overall_score": session.overall_score,
        "next_question": {
            "id": next_question.id,
            "sequence_number": next_question.sequence_number,
            "question_text": next_question.question_text,
            "question_category": next_question.question_category,
            "topic": next_question.topic,
            "difficulty": next_question.difficulty,
            "is_followup": next_question.is_followup,
            "follow_up_rationale": next_question.follow_up_rationale,
        },
    })


@login_required
@require_POST
def skip_question_api(request, session_id: int):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else request.POST
    except Exception:
        body = request.POST

    question_id = int(body.get("question_id", 0) or 0)
    question = get_object_or_404(InterviewQuestion, id=question_id, session=session)
    if not hasattr(question, "response"):
        InterviewResponse.objects.create(
            question=question,
            answer_text="[Question Skipped by Candidate]",
            corrected_answer_text="[Question Skipped by Candidate]",
            input_type="skipped",
            evaluation_data_json=json.dumps({
                "technical_correctness": 0.0,
                "relevance": 0.0,
                "conceptual_understanding": 0.0,
                "completeness": 0.0,
                "clarity": 0.0,
                "communication_quality": 0.0,
                "grammar": 0.0,
                "overall_score": 0.0,
                "overall_evaluation": "Question was skipped by the candidate.",
                "strengths": [],
                "weaknesses": ["Question skipped; review this concept after the session."],
                "missing_concepts": question.get_expected_concepts(),
                "incorrect_statements": [],
                "improved_sample_answer": f"Review key concepts: {', '.join(question.get_expected_concepts())}.",
                "suggestions_for_improvement": ["Attempt foundational definitions even when unsure."],
                "answer_quality_tier": "incorrect",
            }),
            score=0.0,
            feedback="Question skipped by candidate.",
        )

    next_seq = question.sequence_number + 1
    if next_seq > session.max_questions:
        _finalize_interview_session(session)
        return JsonResponse({"status": "interview_completed", "redirect_url": f"/interview/{session.id}/result/"})

    prev_questions = [q.question_text for q in session.questions.all()]
    resume_text = session.resume.extracted_text if session.resume else ""
    projects = session.resume.get_extracted_metadata().get("projects", []) if session.resume else []

    next_q_data = call_fastapi_generate_question({
        "domain": session.domain,
        "subtopics": session.get_subtopics(),
        "skills": session.get_selected_skills(),
        "interview_type": session.interview_type,
        "difficulty": session.current_difficulty,
        "resume_text": resume_text,
        "projects": projects,
        "previous_questions": prev_questions,
        "conversation_history": [],
        "question_number": next_seq,
        "max_questions": session.max_questions,
        "duration_minutes": session.duration_minutes,
    })

    next_question = InterviewQuestion.objects.create(
        session=session,
        question_text=next_q_data.get("question_text", ""),
        question_category=next_q_data.get("question_category", "Conceptual"),
        topic=next_q_data.get("topic", session.domain),
        difficulty=next_q_data.get("difficulty", session.current_difficulty),
        sequence_number=next_seq,
        is_followup=False,
        follow_up_rationale="Pivoted to a new topic after skipped question.",
        expected_concepts_json=json.dumps(next_q_data.get("expected_key_concepts", [])),
    )

    return JsonResponse({
        "status": "next_question_ready",
        "next_question": {
            "id": next_question.id,
            "sequence_number": next_question.sequence_number,
            "question_text": next_question.question_text,
            "question_category": next_question.question_category,
            "topic": next_question.topic,
            "difficulty": next_question.difficulty,
            "is_followup": False,
            "follow_up_rationale": next_question.follow_up_rationale,
        },
    })


@login_required
@require_POST
def toggle_pause_api(request, session_id: int):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    if session.status == "in_progress":
        session.status = "paused"
    elif session.status == "paused":
        session.status = "in_progress"
    session.save()
    return JsonResponse({"status": session.status})


def _finalize_interview_session(session: InterviewSession):
    profile = _ensure_profile(session.user)
    qa_records = []
    for q in session.questions.all().order_by("sequence_number"):
        if hasattr(q, "response"):
            ev = q.response.get_evaluation_data()
            qa_records.append({
                "question_number": q.sequence_number,
                "question_text": q.question_text,
                "topic": q.topic,
                "category": q.question_category,
                "difficulty": q.difficulty,
                "answer_text": q.response.answer_text,
                "overall_score": q.response.score,
                "technical_correctness": q.response.technical_score,
                "conceptual_understanding": q.response.conceptual_score,
                "relevance": q.response.relevance_score,
                "completeness": q.response.completeness_score,
                "communication_quality": q.response.communication_score,
                "grammar": q.response.grammar_score,
                "missing_concepts": ev.get("missing_concepts", []),
            })

    report = call_fastapi_final_report({
        "candidate_name": profile.full_name,
        "domain": session.domain,
        "interview_type": session.interview_type,
        "difficulty": session.current_difficulty,
        "duration_minutes": session.duration_minutes,
        "qa_records": qa_records,
    })

    session.overall_score = float(report.get("overall_score", session.overall_score))
    session.final_report_json = json.dumps(report)
    session.status = "completed"
    session.end_time = timezone.now()
    session.save()


@login_required
def end_interview_view(request, session_id: int):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    if session.status != "completed":
        _finalize_interview_session(session)
    return redirect("interview_result", session_id=session.id)


# =============================================================================
# PAGE 10: Interview Result & Performance Report (Module 11)
# =============================================================================
@login_required
def interview_result_view(request, session_id: int):
    session = get_object_or_404(InterviewSession, id=session_id)
    if session.user != request.user and _ensure_profile(request.user).role != "recruiter":
        return HttpResponseForbidden("Access denied: You cannot access another candidate's interview report.")

    if session.status != "completed":
        _finalize_interview_session(session)

    profile = _ensure_profile(session.user)
    report = session.get_final_report()

    qa_items = []
    for q in session.questions.all().order_by("sequence_number"):
        if hasattr(q, "response"):
            qa_items.append({
                "question": q,
                "response": q.response,
                "eval": q.response.get_evaluation_data(),
            })

    radar_scores = [
        report.get("technical_knowledge", 0),
        report.get("conceptual_understanding", 0),
        report.get("problem_solving_ability", 0),
        report.get("communication", 0),
        report.get("grammar", 0),
        report.get("answer_completeness", 0),
    ]

    return render(request, "core/interview_result.html", {
        "session": session,
        "profile": profile,
        "report": report,
        "qa_items": qa_items,
        "radar_scores_json": json.dumps(radar_scores),
    })


# =============================================================================
# PAGE 11 & 12: Interview History & Performance Analytics (Module 12)
# =============================================================================
@login_required
def interview_history_view(request):
    sessions = InterviewSession.objects.filter(user=request.user).order_by("-start_time")
    return render(request, "core/interview_history.html", {
        "sessions": sessions,
    })


@login_required
def performance_analytics_view(request):
    profile = _ensure_profile(request.user)
    completed = list(InterviewSession.objects.filter(user=request.user, status="completed").order_by("start_time"))

    # 1. Interview Score Trends
    trend_labels = [f"#{s.id} ({s.start_time.strftime('%d %b')})" for s in completed]
    trend_scores = [round(s.overall_score, 2) for s in completed]

    # 2. Domain-wise Performance
    domain_buckets = {}
    for s in completed:
        domain_buckets.setdefault(s.domain, []).append(s.overall_score)
    domain_labels = list(domain_buckets.keys())
    domain_averages = [round(sum(vals) / len(vals), 2) for vals in domain_buckets.values()]

    # 3. Technical Skill & Dimension Performance from real responses
    responses = InterviewResponse.objects.filter(question__session__user=request.user).exclude(input_type="skipped")
    resp_count = responses.count()
    if resp_count > 0:
        dim_averages = [
            round(sum(r.technical_score for r in responses) / resp_count, 2),
            round(sum(r.conceptual_score for r in responses) / resp_count, 2),
            round(sum(r.relevance_score for r in responses) / resp_count, 2),
            round(sum(r.completeness_score for r in responses) / resp_count, 2),
            round(sum(r.communication_score for r in responses) / resp_count, 2),
            round(sum(r.grammar_score for r in responses) / resp_count, 2),
        ]
    else:
        dim_averages = [0, 0, 0, 0, 0, 0]

    # 4. Communication vs Technical Trajectory
    comm_trend = []
    tech_trend = []
    for s in completed:
        rep = s.get_final_report()
        comm_trend.append(round(float(rep.get("communication", s.overall_score)), 2))
        tech_trend.append(round(float(rep.get("technical_knowledge", s.overall_score)), 2))

    return render(request, "core/performance_analytics.html", {
        "profile": profile,
        "completed_count": len(completed),
        "responses_count": resp_count,
        "trend_labels_json": json.dumps(trend_labels),
        "trend_scores_json": json.dumps(trend_scores),
        "domain_labels_json": json.dumps(domain_labels),
        "domain_averages_json": json.dumps(domain_averages),
        "dim_averages_json": json.dumps(dim_averages),
        "comm_trend_json": json.dumps(comm_trend),
        "tech_trend_json": json.dumps(tech_trend),
    })


# =============================================================================
# PAGE 13, 14, 15, 16: Recruiter Candidate Screening & Comparison (Module 10)
# =============================================================================
@login_required
def recruiter_dashboard_view(request):
    profile = _ensure_profile(request.user)
    jobs = ScreeningJob.objects.filter(recruiter=request.user)
    total_screenings = CandidateScreening.objects.filter(job__recruiter=request.user).count()
    recent_screenings = CandidateScreening.objects.filter(job__recruiter=request.user).select_related("job", "resume")[:8]

    return render(request, "core/recruiter_dashboard.html", {
        "profile": profile,
        "jobs": jobs,
        "total_screenings": total_screenings,
        "recent_screenings": recent_screenings,
    })


@login_required
def job_create_view(request):
    profile = _ensure_profile(request.user)
    if request.method == "POST":
        job_title = request.POST.get("job_title", "").strip()
        job_description = request.POST.get("job_description", "").strip()
        req_skills = [s.strip() for s in request.POST.get("required_skills", "").split(",") if s.strip()]
        pref_quals = [s.strip() for s in request.POST.get("preferred_qualifications", "").split(",") if s.strip()]
        min_exp = float(request.POST.get("minimum_experience_years", 0) or 0)
        edu_req = request.POST.get("educational_requirements", "B.Tech / B.E. in Computer Science or related discipline").strip()

        if not job_title or not job_description:
            messages.error(request, "Job title and job description are required.")
            return render(request, "core/job_create.html")

        job = ScreeningJob.objects.create(
            recruiter=request.user,
            job_title=job_title,
            job_description=job_description,
            required_skills_json=json.dumps(req_skills),
            preferred_qualifications_json=json.dumps(pref_quals),
            minimum_experience_years=min_exp,
            educational_requirements=edu_req,
        )
        messages.success(request, f"Created job requisition '{job_title}'. You can now upload candidate resumes for AI screening.")
        return redirect("candidate_screening", job_id=job.id)

    return render(request, "core/job_create.html", {"profile": profile})


@login_required
def candidate_screening_view(request, job_id: int):
    job = get_object_or_404(ScreeningJob, id=job_id, recruiter=request.user)
    screenings = CandidateScreening.objects.filter(job=job).select_related("resume")

    if request.method == "POST":
        uploaded_files = request.FILES.getlist("candidate_resumes")
        pasted_candidate_text = request.POST.get("pasted_candidate_resume", "").strip()

        processed_count = 0
        for uf in uploaded_files:
            try:
                fbytes = uf.read()
                extracted = call_fastapi_extract_resume(fbytes, uf.name)
                raw_text = extracted.get("raw_text", "")
                cand_name = extracted.get("candidate_name") or uf.name.rsplit(".", 1)[0]

                res_obj = Resume.objects.create(
                    user=request.user,
                    file=uf,
                    original_filename=uf.name,
                    extracted_text=raw_text,
                    extracted_skills_json=json.dumps(extracted.get("technical_skills", [])),
                    extracted_metadata_json=json.dumps(extracted),
                    extraction_status="Screened",
                    is_active=False,
                )

                screen_report = call_fastapi_screen_candidate({
                    "job_title": job.job_title,
                    "job_description": job.job_description,
                    "required_skills": job.get_required_skills(),
                    "preferred_qualifications": job.get_preferred_qualifications(),
                    "minimum_experience_years": job.minimum_experience_years,
                    "educational_requirements": job.educational_requirements,
                    "resume_text": raw_text,
                    "extracted_resume": extracted,
                })

                CandidateScreening.objects.create(
                    job=job,
                    resume=res_obj,
                    candidate_name=screen_report.get("candidate_name", cand_name),
                    match_score=float(screen_report.get("job_match_percentage", 0.0)),
                    screening_report_json=json.dumps(screen_report),
                )
                processed_count += 1
            except Exception as exc:
                messages.error(request, f"Could not screen '{uf.name}': {exc}")

        if pasted_candidate_text:
            try:
                extracted = call_fastapi_extract_resume(pasted_candidate_text.encode("utf-8"), "candidate_resume.txt")
                res_obj = Resume.objects.create(
                    user=request.user,
                    original_filename="pasted_candidate_resume.txt",
                    extracted_text=pasted_candidate_text,
                    extracted_skills_json=json.dumps(extracted.get("technical_skills", [])),
                    extracted_metadata_json=json.dumps(extracted),
                    extraction_status="Screened",
                    is_active=False,
                )
                screen_report = call_fastapi_screen_candidate({
                    "job_title": job.job_title,
                    "job_description": job.job_description,
                    "required_skills": job.get_required_skills(),
                    "preferred_qualifications": job.get_preferred_qualifications(),
                    "minimum_experience_years": job.minimum_experience_years,
                    "educational_requirements": job.educational_requirements,
                    "resume_text": pasted_candidate_text,
                    "extracted_resume": extracted,
                })
                CandidateScreening.objects.create(
                    job=job,
                    resume=res_obj,
                    candidate_name=screen_report.get("candidate_name", "Candidate"),
                    match_score=float(screen_report.get("job_match_percentage", 0.0)),
                    screening_report_json=json.dumps(screen_report),
                )
                processed_count += 1
            except Exception as exc:
                messages.error(request, f"Error screening pasted resume: {exc}")

        if processed_count:
            messages.success(request, f"Successfully screened {processed_count} candidate resume(s) against '{job.job_title}'.")
            return redirect("candidate_screening", job_id=job.id)

    return render(request, "core/candidate_screening.html", {
        "job": job,
        "screenings": screenings,
    })


@login_required
def candidate_comparison_view(request, job_id: int):
    job = get_object_or_404(ScreeningJob, id=job_id, recruiter=request.user)
    screenings = list(CandidateScreening.objects.filter(job=job).order_by("-match_score"))

    chart_labels = [s.candidate_name for s in screenings]
    chart_matches = [round(s.match_score, 1) for s in screenings]
    chart_skills_scores = [
        round(s.get_screening_report().get("category_scores", {}).get("required_skills_match", s.match_score), 1)
        for s in screenings
    ]
    chart_project_scores = [
        round(s.get_screening_report().get("category_scores", {}).get("project_relevance", s.match_score), 1)
        for s in screenings
    ]

    return render(request, "core/candidate_comparison.html", {
        "job": job,
        "screenings": screenings,
        "chart_labels_json": json.dumps(chart_labels),
        "chart_matches_json": json.dumps(chart_matches),
        "chart_skills_scores_json": json.dumps(chart_skills_scores),
        "chart_project_scores_json": json.dumps(chart_project_scores),
    })
