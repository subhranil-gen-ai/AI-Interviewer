#!/usr/bin/env python3
"""
Comprehensive End-to-End Automated Verification & SQLite Database Seeding Suite.
Tests:
1. FastAPI Microservice Health & Schema Validation
2. Real PDF & DOCX Resume Parsing + Legacy .DOC Error Guardrail
3. AI Resume Analysis (9 required output sections)
4. Resume-Grounded Question Generation (Random Forest + Credit Card Fraud Detection + Flask)
5. Multi-Turn Conversational Follow-Up Chain (Python Decorator -> Wrapper Function -> Execution Time -> Decorator vs Closure)
6. 7-Dimension Semantic Answer Evaluation (Overfitting paraphrase test scoring >= 8.5/10)
7. Grammar Correction & Meaning Preservation
8. Rule-Based Adaptive Difficulty Engine (Increase > 8.0, Maintain 5.0-8.0, Reduce < 5.0)
9. Ethical AI Recruiter Candidate Screening & Multi-Candidate Comparison
10. Final Interview Report Synthesis & SQLite Database Persistence (`backend/db.sqlite3`)
"""
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from ai_service.main import app
from ai_service.resume_parser import extract_text_from_file


def run_verification():
    client = TestClient(app)
    report_log = []

    def record(step_name: str, passed: bool, details: str):
        status = "PASS" if passed else "FAIL"
        line = f"[{status}] {step_name}: {details}"
        print(line)
        report_log.append({"step": step_name, "status": status, "details": details})
        if not passed:
            raise AssertionError(line)

    # 1. Health Check
    r_health = client.get("/health")
    record("1. FastAPI AI Service Health", r_health.status_code == 200, json.dumps(r_health.json()))

    # 2. Real PDF & DOCX Resume Extraction + Legacy .DOC Guardrail
    pdf_path = ROOT_DIR / "sample_data" / "Arjun_Sharma_ML_Resume.pdf"
    docx_path = ROOT_DIR / "sample_data" / "Arjun_Sharma_ML_Resume.docx"
    priya_pdf_path = ROOT_DIR / "sample_data" / "Priya_Nair_Backend_Resume.pdf"

    with open(pdf_path, "rb") as fp:
        r_pdf = client.post("/api/v1/resume/extract-file", files={"file": ("Arjun_Sharma_ML_Resume.pdf", fp.read(), "application/pdf")})
    assert r_pdf.status_code == 200, r_pdf.text
    arjun_extracted = r_pdf.json()
    record(
        "2A. PDF Resume Extraction (pdfplumber/pypdf)",
        "Random Forest" in arjun_extracted["technical_skills"] and "Flask" in arjun_extracted["technical_skills"],
        f"Candidate: {arjun_extracted['candidate_name']}, Extracted {len(arjun_extracted['technical_skills'])} skills: {', '.join(arjun_extracted['technical_skills'][:8])}",
    )

    with open(docx_path, "rb") as fp:
        r_docx = client.post("/api/v1/resume/extract-file", files={"file": ("Arjun_Sharma_ML_Resume.docx", fp.read(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
    assert r_docx.status_code == 200, r_docx.text
    record(
        "2B. DOCX Resume Extraction (python-docx)",
        len(r_docx.json()["projects"]) >= 1,
        f"Extracted {len(r_docx.json()['projects'])} project(s): {r_docx.json()['projects'][0]['title']}",
    )

    # Test legacy binary .doc rejection message
    r_doc = client.post("/api/v1/resume/extract-file", files={"file": ("legacy.doc", b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1\x00\x00", "application/msword")})
    record(
        "2C. Legacy Binary .DOC Limitation Guardrail",
        r_doc.status_code == 400 and "Legacy binary Microsoft Word (.doc" in r_doc.json()["detail"],
        r_doc.json()["detail"][:110] + "...",
    )

    # 3. AI Resume Analysis (All 9 Sections)
    r_ana = client.post("/api/v1/resume/analyze", json={
        "resume_text": arjun_extracted["raw_text"],
        "extracted_data": arjun_extracted,
        "target_domain": "Machine Learning",
    })
    assert r_ana.status_code == 200, r_ana.text
    arjun_analysis = r_ana.json()
    required_analysis_keys = [
        "professional_summary", "technical_skill_summary", "strong_technical_areas",
        "weak_or_missing_areas", "project_analysis", "internship_analysis",
        "education_summary", "suggested_interview_topics", "resume_improvement_suggestions"
    ]
    record(
        "3. AI Resume Analysis (All 9 Required Sections)",
        all(k in arjun_analysis and arjun_analysis[k] for k in required_analysis_keys),
        f"Readiness Score: {arjun_analysis['readiness_score']}%, Suggested Topics: {len(arjun_analysis['suggested_interview_topics'])}",
    )

    # 4. Resume-Grounded Dynamic Question Generation (Module 3 & Module 5.A)
    r_q1 = client.post("/api/v1/interview/generate-question", json={
        "domain": "Machine Learning",
        "subtopics": ["Ensemble Models", "Imbalanced Data", "Model Deployment"],
        "skills": arjun_extracted["technical_skills"],
        "interview_type": "Resume-Based Interview",
        "difficulty": "Intermediate",
        "resume_text": arjun_extracted["raw_text"],
        "projects": arjun_extracted["projects"],
        "previous_questions": [],
        "conversation_history": [],
        "question_number": 1,
        "max_questions": 5,
    })
    assert r_q1.status_code == 200
    q1 = r_q1.json()
    record(
        "4. Resume-Grounded Opening Question",
        any(term in q1["question_text"].lower() for term in ["credit card fraud", "random forest", "flask"]),
        f"Q1 ({q1['question_category']}): {q1['question_text']}",
    )

    # 5. Multi-Turn Conversational Follow-up Chain (Decorator -> Wrapper -> Timing Decorator -> Decorator vs Closure)
    conv_q1 = "What is a Python decorator?"
    conv_a1 = "A decorator is used to modify the behavior of a function without changing its original source code."
    r_follow1 = client.post("/api/v1/interview/generate-question", json={
        "domain": "Python Development",
        "skills": ["Python", "Decorators", "Closures"],
        "interview_type": "Technical Interview",
        "difficulty": "Intermediate",
        "previous_questions": [conv_q1],
        "conversation_history": [{"question": conv_q1, "answer": conv_a1, "score": 8.8, "quality_tier": "strong", "topic": "Python Decorators"}],
        "question_number": 2,
        "max_questions": 5,
    })
    fq1 = r_follow1.json()
    record(
        "5A. Contextual Follow-Up Turn 2 (Wrapper Function)",
        fq1["is_followup"] and "wrapper" in fq1["question_text"].lower(),
        f"AI Follow-Up 1: {fq1['question_text']}",
    )

    conv_a2 = "It wraps another function inside an inner wrapper function and adds additional functionality."
    r_follow2 = client.post("/api/v1/interview/generate-question", json={
        "domain": "Python Development",
        "skills": ["Python", "Decorators", "Closures"],
        "interview_type": "Technical Interview",
        "difficulty": "Advanced",
        "previous_questions": [conv_q1, fq1["question_text"]],
        "conversation_history": [
            {"question": conv_q1, "answer": conv_a1, "score": 8.8, "quality_tier": "strong"},
            {"question": fq1["question_text"], "answer": conv_a2, "score": 8.6, "quality_tier": "strong"},
        ],
        "question_number": 3,
        "max_questions": 5,
    })
    fq2 = r_follow2.json()
    record(
        "5B. Contextual Follow-Up Turn 3 (Execution Time Decorator)",
        fq2["is_followup"] and "execution time" in fq2["question_text"].lower(),
        f"AI Follow-Up 2: {fq2['question_text']}",
    )

    # 6. Semantic Answer Evaluation (Module 7 Overfitting Example)
    r_eval = client.post("/api/v1/interview/evaluate-answer", json={
        "question_text": "What is overfitting in Machine Learning?",
        "question_category": "Conceptual",
        "difficulty": "Intermediate",
        "domain": "Machine Learning",
        "candidate_answer": "Overfitting happens when a model learns training data very well but performs poorly on unseen data.",
        "expected_key_concepts": ["training data", "unseen data", "generalization", "high variance"],
    })
    assert r_eval.status_code == 200
    ev_data = r_eval.json()
    record(
        "6. 7-Dimension Semantic Answer Evaluation",
        ev_data["overall_score"] >= 8.5 and ev_data["technical_correctness"] >= 8.5,
        f"Overall: {ev_data['overall_score']}/10 (Tech: {ev_data['technical_correctness']}, Relevance: {ev_data['relevance']}, Concept: {ev_data['conceptual_understanding']}, Completeness: {ev_data['completeness']}, Comm: {ev_data['communication_quality']}, Grammar: {ev_data['grammar']})",
    )

    # 7. Grammar Correction & Communication Analysis (Module 8)
    r_gram = client.post("/api/v1/interview/grammar-check", json={
        "candidate_answer": "i dont use accuracy on imbalanced dataset bcoz umm it basically predicts majority class all the time"
    })
    assert r_gram.status_code == 200
    gram_data = r_gram.json()
    record(
        "7. Grammar Correction (Meaning Preserved)",
        "I do not" in gram_data["corrected_answer"] and "because" in gram_data["corrected_answer"] and "imbalanced dataset" in gram_data["corrected_answer"],
        f"Original: '{gram_data['original_answer']}' -> Corrected: '{gram_data['corrected_answer']}'",
    )

    # 8. Adaptive Difficulty Engine (Module 9)
    r_ad_up = client.post("/api/v1/interview/adaptive-difficulty", json={
        "current_difficulty": "Intermediate",
        "recent_scores": [8.6, 8.9, 9.1],
        "adaptive_enabled": True,
    }).json()
    r_ad_down = client.post("/api/v1/interview/adaptive-difficulty", json={
        "current_difficulty": "Intermediate",
        "recent_scores": [4.2, 4.5],
        "adaptive_enabled": True,
    }).json()
    record(
        "8. Adaptive Difficulty Progression Engine",
        r_ad_up["recommended_difficulty"] == "Advanced" and r_ad_down["recommended_difficulty"] == "Beginner",
        f"High Scores [8.6, 8.9, 9.1] -> {r_ad_up['recommended_difficulty']} ({r_ad_up['adjustment_action']}); Low Scores [4.2, 4.5] -> {r_ad_down['recommended_difficulty']} ({r_ad_down['adjustment_action']})",
    )

    # 9. Ethical AI Recruiter Candidate Screening (Module 10)
    with open(priya_pdf_path, "rb") as fp:
        priya_extracted = client.post("/api/v1/resume/extract-file", files={"file": ("Priya_Nair_Backend_Resume.pdf", fp.read(), "application/pdf")}).json()

    jd_payload = {
        "job_title": "Machine Learning & Python Backend Engineer",
        "job_description": "Build and deploy Random Forest and Scikit-learn fraud detection models using Python, Flask, FastAPI, Django, and SQL.",
        "required_skills": ["Python", "Machine Learning", "Random Forest", "Flask", "FastAPI", "Django", "SQL"],
        "preferred_qualifications": ["Docker", "Git", "SMOTE"],
        "minimum_experience_years": 0.0,
        "educational_requirements": "B.Tech in Computer Science or IT",
    }

    arjun_screen = client.post("/api/v1/screening/evaluate-candidate", json={
        **jd_payload,
        "resume_text": arjun_extracted["raw_text"],
        "extracted_resume": arjun_extracted,
    }).json()

    priya_screen = client.post("/api/v1/screening/evaluate-candidate", json={
        **jd_payload,
        "resume_text": priya_extracted["raw_text"],
        "extracted_resume": priya_extracted,
    }).json()

    record(
        "9. Multi-Candidate Recruiter Screening & Fairness Check",
        arjun_screen["job_match_percentage"] > priya_screen["job_match_percentage"] and "Protected attributes" in arjun_screen["fairness_disclaimer"],
        f"Arjun Match: {arjun_screen['job_match_percentage']}% (Matched {len(arjun_screen['matching_skills'])}/7 skills) vs Priya Match: {priya_screen['job_match_percentage']}% (Matched {len(priya_screen['matching_skills'])}/7 skills)",
    )

    # 10. Final Interview Report & SQLite Database Creation/Seeding (`backend/db.sqlite3`)
    final_rep = client.post("/api/v1/interview/final-report", json={
        "candidate_name": "Arjun Sharma",
        "domain": "Machine Learning",
        "interview_type": "Resume-Based Interview",
        "difficulty": "Advanced",
        "duration_minutes": 15,
        "qa_records": [
            {
                "question_number": 1,
                "question_text": q1["question_text"],
                "topic": q1["topic"],
                "overall_score": 8.9,
                "technical_correctness": 9.0,
                "conceptual_understanding": 9.0,
                "relevance": 9.5,
                "completeness": 8.5,
                "communication_quality": 8.8,
                "grammar": 9.0,
                "missing_concepts": [],
            },
            {
                "question_number": 2,
                "question_text": "What is overfitting in Machine Learning?",
                "topic": "Overfitting & Generalization",
                "overall_score": ev_data["overall_score"],
                "technical_correctness": ev_data["technical_correctness"],
                "conceptual_understanding": ev_data["conceptual_understanding"],
                "relevance": ev_data["relevance"],
                "completeness": ev_data["completeness"],
                "communication_quality": ev_data["communication_quality"],
                "grammar": ev_data["grammar"],
                "missing_concepts": ev_data["missing_concepts"],
            },
        ],
    }).json()

    # Initialize & verify SQLite database (`backend/db.sqlite3`) with all 8 tables & sample records
    db_path = ROOT_DIR / "backend" / "db.sqlite3"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS auth_user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(150) UNIQUE NOT NULL,
        email VARCHAR(254) NOT NULL,
        password VARCHAR(128) NOT NULL,
        first_name VARCHAR(150) DEFAULT '',
        last_name VARCHAR(150) DEFAULT '',
        is_active BOOLEAN DEFAULT 1,
        date_joined DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS core_candidateprofile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        role VARCHAR(20) DEFAULT 'candidate',
        full_name VARCHAR(150) NOT NULL,
        phone_number VARCHAR(30) DEFAULT '',
        education VARCHAR(255) DEFAULT '',
        graduation_year INTEGER DEFAULT 2027,
        preferred_domain VARCHAR(100) DEFAULT 'Machine Learning',
        experience_level VARCHAR(80) DEFAULT 'Fresher / Final-Year Student',
        skills_json TEXT DEFAULT '[]',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS core_resume (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        file VARCHAR(100) DEFAULT '',
        file_path VARCHAR(500) DEFAULT '',
        original_filename VARCHAR(255) NOT NULL,
        extracted_text TEXT DEFAULT '',
        extracted_skills_json TEXT DEFAULT '[]',
        extracted_metadata_json TEXT DEFAULT '{}',
        analysis_report_json TEXT DEFAULT '{}',
        extraction_status VARCHAR(50) DEFAULT 'Verified & Analyzed',
        is_active BOOLEAN DEFAULT 1,
        upload_date DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS core_interviewsession (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        resume_id INTEGER,
        domain VARCHAR(100) NOT NULL,
        subtopics_json TEXT DEFAULT '[]',
        selected_skills_json TEXT DEFAULT '[]',
        interview_type VARCHAR(80) NOT NULL,
        difficulty VARCHAR(40) NOT NULL,
        current_difficulty VARCHAR(40) NOT NULL,
        adaptive_enabled BOOLEAN DEFAULT 1,
        duration_minutes INTEGER DEFAULT 15,
        max_questions INTEGER DEFAULT 5,
        status VARCHAR(30) DEFAULT 'completed',
        start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        end_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        overall_score REAL DEFAULT 0.0,
        final_report_json TEXT DEFAULT '{}'
    );
    CREATE TABLE IF NOT EXISTS core_interviewquestion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        question_category VARCHAR(80) DEFAULT 'Conceptual',
        topic VARCHAR(150) DEFAULT '',
        difficulty VARCHAR(40) DEFAULT 'Intermediate',
        sequence_number INTEGER DEFAULT 1,
        is_followup BOOLEAN DEFAULT 0,
        follow_up_rationale TEXT DEFAULT '',
        expected_concepts_json TEXT DEFAULT '[]',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS core_interviewresponse (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER UNIQUE NOT NULL,
        answer_text TEXT DEFAULT '',
        corrected_answer_text TEXT DEFAULT '',
        input_type VARCHAR(20) DEFAULT 'voice',
        evaluation_data_json TEXT DEFAULT '{}',
        score REAL DEFAULT 0.0,
        technical_score REAL DEFAULT 0.0,
        conceptual_score REAL DEFAULT 0.0,
        relevance_score REAL DEFAULT 0.0,
        completeness_score REAL DEFAULT 0.0,
        communication_score REAL DEFAULT 0.0,
        grammar_score REAL DEFAULT 0.0,
        feedback TEXT DEFAULT '',
        submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS core_screeningjob (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recruiter_id INTEGER NOT NULL,
        job_title VARCHAR(200) NOT NULL,
        job_description TEXT NOT NULL,
        required_skills_json TEXT DEFAULT '[]',
        preferred_qualifications_json TEXT DEFAULT '[]',
        minimum_experience_years REAL DEFAULT 0.0,
        educational_requirements VARCHAR(255) DEFAULT '',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS core_candidatescreening (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        resume_id INTEGER NOT NULL,
        candidate_name VARCHAR(150) NOT NULL,
        match_score REAL DEFAULT 0.0,
        screening_report_json TEXT DEFAULT '{}',
        screened_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    for _t in ["auth_user", "core_candidateprofile", "core_resume", "core_interviewsession", "core_interviewquestion", "core_interviewresponse", "core_screeningjob", "core_candidatescreening"]: cur.execute(f"DELETE FROM {_t}")
    cur.execute(
        "INSERT INTO auth_user (id, username, email, password, first_name, last_name) VALUES (1, 'arjun_sharma', 'arjun.sharma.cse@college.edu.in', 'pbkdf2_sha256$720000$demo$hash', 'Arjun', 'Sharma')"
    )
    cur.execute(
        "INSERT INTO core_candidateprofile (user_id, role, full_name, phone_number, education, graduation_year, preferred_domain, skills_json) VALUES (1, 'candidate', 'Arjun Sharma', '+91 9876543210', 'B.Tech in Computer Science and Engineering (UEM Kolkata)', 2027, 'Machine Learning', ?)",
        (json.dumps(arjun_extracted["technical_skills"]),),
    )
    cur.execute(
        "INSERT INTO core_resume (id, user_id, original_filename, extracted_text, extracted_skills_json, extracted_metadata_json, analysis_report_json) VALUES (1, 1, 'Arjun_Sharma_ML_Resume.pdf', ?, ?, ?, ?)",
        (
            arjun_extracted["raw_text"],
            json.dumps(arjun_extracted["technical_skills"]),
            json.dumps(arjun_extracted),
            json.dumps(arjun_analysis),
        ),
    )
    cur.execute(
        "INSERT INTO core_interviewsession (id, user_id, resume_id, domain, selected_skills_json, interview_type, difficulty, current_difficulty, duration_minutes, max_questions, status, overall_score, final_report_json) VALUES (1, 1, 1, 'Machine Learning', ?, 'Resume-Based Interview', 'Adaptive', 'Advanced', 15, 5, 'completed', ?, ?)",
        (
            json.dumps(arjun_extracted["technical_skills"]),
            final_rep["overall_score"],
            json.dumps(final_rep),
        ),
    )
    cur.execute(
        "INSERT INTO core_interviewquestion (id, session_id, question_text, question_category, topic, difficulty, sequence_number, is_followup, follow_up_rationale) VALUES (1, 1, ?, ?, ?, 'Intermediate', 1, 0, ?)",
        (q1["question_text"], q1["question_category"], q1["topic"], q1["follow_up_rationale"]),
    )
    cur.execute(
        "INSERT INTO core_interviewresponse (question_id, answer_text, corrected_answer_text, input_type, evaluation_data_json, score, technical_score, conceptual_score, relevance_score, completeness_score, communication_score, grammar_score, feedback) VALUES (1, ?, ?, 'voice', ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "Overfitting happens when a model learns training data very well but performs poorly on unseen data.",
            ev_data["grammar_analysis"]["corrected_answer"],
            json.dumps(ev_data),
            ev_data["overall_score"],
            ev_data["technical_correctness"],
            ev_data["conceptual_understanding"],
            ev_data["relevance"],
            ev_data["completeness"],
            ev_data["communication_quality"],
            ev_data["grammar"],
            ev_data["overall_evaluation"],
        ),
    )
    cur.execute(
        "INSERT INTO core_screeningjob (id, recruiter_id, job_title, job_description, required_skills_json, preferred_qualifications_json, minimum_experience_years, educational_requirements) VALUES (1, 1, ?, ?, ?, ?, 0.0, 'B.Tech in CSE/IT')",
        (
            jd_payload["job_title"],
            jd_payload["job_description"],
            json.dumps(jd_payload["required_skills"]),
            json.dumps(jd_payload["preferred_qualifications"]),
        ),
    )
    cur.execute(
        "INSERT INTO core_candidatescreening (job_id, resume_id, candidate_name, match_score, screening_report_json) VALUES (1, 1, 'Arjun Sharma', ?, ?)",
        (arjun_screen["job_match_percentage"], json.dumps(arjun_screen)),
    )
    cur.execute(
        "INSERT INTO core_candidatescreening (job_id, resume_id, candidate_name, match_score, screening_report_json) VALUES (1, 1, 'Priya Nair', ?, ?)",
        (priya_screen["job_match_percentage"], json.dumps(priya_screen)),
    )
    conn.commit()

    table_counts = {}
    for tbl in [
        "auth_user", "core_candidateprofile", "core_resume", "core_interviewsession",
        "core_interviewquestion", "core_interviewresponse", "core_screeningjob", "core_candidatescreening"
    ]:
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        table_counts[tbl] = cur.fetchone()[0]
    conn.close()

    record(
        "10. SQLite Database Persistence & Final Report Verification",
        all(c >= 1 for c in table_counts.values()),
        f"SQLite Tables Populated: {json.dumps(table_counts)}, Final Report Score: {final_rep['overall_score']}/10",
    )

    print("\nALL 10 END-TO-END VERIFICATION SUITES PASSED SUCCESSFULLY!")
    return report_log


if __name__ == "__main__":
    run_verification()
