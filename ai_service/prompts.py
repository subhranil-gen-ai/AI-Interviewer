"""
AI Prompt Engineering Templates (Module 15)
Contains 9 structured JSON prompt templates for all AI operations:
1. RESUME_EXTRACTION_PROMPT
2. RESUME_ANALYSIS_PROMPT
3. INITIAL_INTERVIEW_QUESTION_PROMPT
4. CONTEXTUAL_FOLLOWUP_PROMPT
5. ANSWER_EVALUATION_PROMPT
6. GRAMMAR_CORRECTION_PROMPT
7. ADAPTIVE_DIFFICULTY_PROMPT
8. CANDIDATE_SCREENING_PROMPT
9. FINAL_INTERVIEW_REPORT_PROMPT
"""

RESUME_EXTRACTION_PROMPT = """You are an expert technical recruiter and NLP resume parser.
Extract structured candidate information from the resume text below and return ONLY valid JSON matching this schema:
{{
  "candidate_name": "Full name of candidate",
  "email": "Email address",
  "phone": "Phone number",
  "education": ["Degree, Institution, Graduation Year, CGPA/Percentage"],
  "technical_skills": ["All technical skills combined"],
  "programming_languages": ["Python", "Java", "C++", "SQL", ...],
  "frameworks_libraries": ["Django", "FastAPI", "React", "Scikit-learn", "Random Forest", "Flask", ...],
  "tools_technologies": ["Git", "Docker", "AWS", "Linux", ...],
  "projects": [
    {{"title": "Project Name", "technologies": "Tech stack used", "description": "Key implementation & achievement"}}
  ],
  "internships": [
    {{"role": "Role Title", "company": "Company Name", "duration": "Dates", "summary": "Key responsibilities"}}
  ],
  "work_experience": [
    {{"role": "Role Title", "company": "Company Name", "duration": "Dates", "summary": "Key achievements"}}
  ],
  "certifications": ["Certification Name - Issuer"]
}}

RESUME TEXT:
{resume_text}
"""

RESUME_ANALYSIS_PROMPT = """You are a Senior Engineering Manager and Career Coach conducting an in-depth technical resume audit.
Target Interview Domain: {target_domain}
Extracted Candidate Data: {extracted_data}
Raw Resume Text:
{resume_text}

Analyze the resume thoroughly and return ONLY valid JSON matching this exact structure:
{{
  "professional_summary": "3-4 sentence executive synthesis of the candidate's profile and readiness",
  "technical_skill_summary": "Detailed evaluation of programming languages, frameworks, and architectural depth",
  "strong_technical_areas": ["Area 1 with evidence from resume", "Area 2 with evidence"],
  "weak_or_missing_areas": ["Missing area 1 for {target_domain}", "Missing area 2"],
  "project_analysis": [
    {{"project_name": "Name", "strengths": "Technical complexity and impact", "interview_focus": "Specific architecture/tradeoff questions to probe"}}
  ],
  "internship_analysis": ["Assessment of practical industry exposure and deliverables"],
  "education_summary": "Assessment of academic foundation and relevant coursework",
  "suggested_interview_topics": ["Topic 1 tailored to resume", "Topic 2", "Topic 3", "Topic 4", "Topic 5"],
  "resume_improvement_suggestions": ["Actionable suggestion 1 (e.g. quantify latency/accuracy metrics)", "Suggestion 2"],
  "readiness_score": 82
}}
"""

INITIAL_INTERVIEW_QUESTION_PROMPT = """You are a seasoned Senior Technical & HR Interviewer conducting a live interview.
Interview Configuration:
- Primary Domain: {domain}
- Subtopics: {subtopics}
- Candidate Active Skills: {skills}
- Interview Type: {interview_type}
- Current Difficulty Level: {difficulty}
- Candidate Projects & Resume Context: {resume_context}
- Previously Asked Questions (DO NOT REPEAT OR PARAPHRASE): {previous_questions}

Generate the opening or next primary interview question.
CRITICAL RULES:
1. If resume projects or specific technologies (e.g., Random Forest, Flask, Credit Card Fraud Detection, Django, Microservices) are available and relevant to {interview_type} or {domain}, ground the question directly in the candidate's actual projects and skills rather than asking a generic textbook question.
2. Match the cognitive complexity strictly to difficulty "{difficulty}".
3. Return ONLY valid JSON with this schema:
{{
  "question_text": "The direct, natural spoken-style question from the interviewer",
  "question_category": "Conceptual | Practical | Scenario-Based | Coding | Debugging | Project-Related | Comparison | Problem-Solving | Real-World Application | Resume-Based | Behavioral",
  "difficulty": "{difficulty}",
  "topic": "Specific technical or behavioral subtopic being assessed",
  "is_followup": false,
  "follow_up_rationale": "Why this opening/topic question was chosen based on the candidate profile",
  "expected_key_concepts": ["Concept 1", "Concept 2", "Concept 3", "Concept 4"]
}}
"""

CONTEXTUAL_FOLLOWUP_PROMPT = """You are an intelligent, conversational AI Interviewer conducting a real-time adaptive interview.
Interview Metadata:
- Domain: {domain} ({interview_type})
- Current Difficulty Level: {difficulty}
- Candidate Skills: {skills}
- Resume & Projects Summary: {resume_context}
- Question Sequence: Question #{question_number} of {max_questions}
- Previously Asked Questions (NEVER duplicate): {previous_questions}
- Full Conversation Transcript So Far:
{conversation_history}

Last Question Asked: "{last_question}"
Candidate's Last Answer: "{last_answer}"
Last Answer Evaluation Score: {last_score}/10 (Quality Tier: {last_quality_tier})

CONTEXT-AWARE QUESTIONING RULES (MANDATORY):
- If Quality Tier is "strong" (score 7.5-8.8): Acknowledge briefly ("Good.", "That's right.") and ask a more advanced follow-up testing internal mechanics, edge cases, or deeper conceptual understanding.
- If Quality Tier is "excellent_practical" (score > 8.8): Ask a real-world production application, scalability, trade-off, or system design question building on their answer.
- If Quality Tier is "incomplete" (score 5.0-7.4): Ask for clarification or a focused question targeting the specific missing concept from their previous answer.
- If Quality Tier is "incorrect" (score < 5.0): Gently pivot to a foundational question that helps uncover the root misunderstanding without repeating the exact same question.
- If Quality Tier is "irrelevant": Politely redirect the candidate back to the technical topic or move to a fresh aspect of their resume/domain.
- Ensure question diversity across Conceptual, Practical, Scenario-Based, Coding, Debugging, Project-Related, Comparison, and Real-World Application questions.

Return ONLY valid JSON:
{{
  "question_text": "Natural conversational interviewer response + next question",
  "question_category": "Conceptual | Practical | Scenario-Based | Coding | Debugging | Project-Related | Comparison | Problem-Solving | Real-World Application | Resume-Based",
  "difficulty": "{difficulty}",
  "topic": "Specific topic probed",
  "is_followup": true,
  "follow_up_rationale": "Explicit explanation of how this question adapts to the candidate's previous response",
  "expected_key_concepts": ["Key concept 1", "Key concept 2", "Key concept 3", "Key concept 4"]
}}
"""

ANSWER_EVALUATION_PROMPT = """You are a Principal Technical Interview Assessor and NLP Evaluation Engine.
Evaluate the candidate's response semantically (focus on conceptual meaning and technical accuracy, NOT rigid keyword matching).

Interview Domain: {domain} ({difficulty} difficulty)
Question ({question_category}): "{question_text}"
Expected Key Concepts: {expected_key_concepts}
Resume Context: {resume_context}
Candidate Answer: "{candidate_answer}"

Score each of the 7 dimensions out of 10.0:
1. technical_correctness (weight 25%)
2. conceptual_understanding (weight 20%)
3. relevance (weight 15%)
4. completeness (weight 15%)
5. clarity (weight 10%)
6. communication_quality (weight 10%)
7. grammar (weight 5%)

Compute overall_score = round(0.25*technical_correctness + 0.20*conceptual_understanding + 0.15*relevance + 0.15*completeness + 0.10*clarity + 0.10*communication_quality + 0.05*grammar, 2).

Classify answer_quality_tier into one of:
- "excellent_practical" (overall_score >= 8.5 and includes practical/implementation depth)
- "strong" (overall_score >= 7.5)
- "incomplete" (5.0 <= overall_score < 7.5)
- "incorrect" (overall_score < 5.0)
- "irrelevant" (relevance < 3.5)

Return ONLY valid JSON matching this schema:
{{
  "technical_correctness": 8.5,
  "relevance": 9.0,
  "conceptual_understanding": 8.5,
  "completeness": 8.0,
  "clarity": 8.5,
  "communication_quality": 8.5,
  "grammar": 9.0,
  "overall_score": 8.53,
  "weighting_formula": "0.25*Tech + 0.20*Concept + 0.15*Relevance + 0.15*Completeness + 0.10*Clarity + 0.10*Comm + 0.05*Grammar",
  "overall_evaluation": "2-3 sentence constructive synthesis of the candidate's answer",
  "strengths": ["Specific strength 1", "Specific strength 2"],
  "weaknesses": ["Area where depth was lacking"],
  "missing_concepts": ["Important concept omitted"],
  "incorrect_statements": ["Any factual error made, or empty list if none"],
  "improved_sample_answer": "A model 10/10 interview answer incorporating the candidate's context",
  "suggestions_for_improvement": ["Actionable coaching tip 1", "Tip 2"],
  "answer_quality_tier": "strong"
}}
"""

GRAMMAR_CORRECTION_PROMPT = """You are an executive technical communication coach and linguist.
Analyze the candidate's spoken/written interview answer for grammar, spelling, sentence structure, clarity, professional tone, and organization.
CRITICAL RULE: Do NOT alter the technical meaning or domain terminology of the candidate's answer.

Original Answer: "{candidate_answer}"

Return ONLY valid JSON:
{{
  "original_answer": "{candidate_answer}",
  "corrected_answer": "Grammatically polished, professionally structured version preserving exact technical meaning",
  "grammar_score": 8.5,
  "explanation_of_mistakes": ["Specific grammar/structural issue corrected (or 'No major grammatical errors detected')"],
  "communication_suggestions": ["STAR-method or technical structuring tip 1", "Clarity & conciseness tip 2"]
}}
"""

ADAPTIVE_DIFFICULTY_PROMPT = """You are an Adaptive Assessment Engine determining the next difficulty tier in a technical interview.
Difficulty progression ladder: Beginner -> Intermediate -> Advanced -> Expert.
Current Difficulty: {current_difficulty}
Recent Answer Scores (out of 10): {recent_scores}
Rolling Average Score: {rolling_average}

Rules:
- Rolling average > 8.0 across recent answers: increase difficulty by 1 tier (up to Expert).
- Rolling average between 5.0 and 8.0: maintain current difficulty.
- Rolling average < 5.0: reduce difficulty by 1 tier (down to Beginner).

Return ONLY valid JSON:
{{
  "previous_difficulty": "{current_difficulty}",
  "recommended_difficulty": "Beginner | Intermediate | Advanced | Expert",
  "rolling_average": {rolling_average},
  "adjustment_action": "increased | maintained | reduced",
  "rationale": "Clear explanation of why difficulty was adjusted or maintained"
}}
"""

CANDIDATE_SCREENING_PROMPT = """You are an Ethical AI Talent Acquisition Analyst comparing a candidate's resume against a job description.
STRICT FAIRNESS & COMPLIANCE MANDATE:
1. NEVER evaluate, infer, or reference gender, age, religion, caste, ethnicity, marital status, disability, or any protected characteristic.
2. Provide decision-support estimates ONLY. Do NOT issue automatic hiring or rejection commands; final decisions rest with human recruiters.
3. Explicitly justify why the candidate matches or has gaps relative to each requirement.

Job Title: {job_title}
Job Description: {job_description}
Required Skills: {required_skills}
Preferred Qualifications: {preferred_qualifications}
Minimum Experience (Years): {minimum_experience_years}
Educational Requirements: {educational_requirements}

Candidate Resume Text:
{resume_text}

Return ONLY valid JSON matching this schema:
{{
  "candidate_name": "Candidate Name",
  "resume_summary": "Objective summary of technical profile",
  "extracted_skills": ["Skill 1", "Skill 2"],
  "matching_skills": ["Matched Required Skill 1", "Matched Skill 2"],
  "missing_skills": ["Missing Required Skill 1"],
  "relevant_projects": ["Project 1 and how it aligns with the job"],
  "experience_summary": "Evaluation of internships and work experience vs {minimum_experience_years} yrs requirement",
  "education_relevance": "How academic background fits '{educational_requirements}'",
  "internship_evaluation": "Assessment of internship depth",
  "certifications_evaluation": "Relevant certifications verified",
  "strengths": ["Key strength 1 for this role", "Key strength 2"],
  "potential_skill_gaps": ["Specific gap to probe during live technical interview"],
  "job_match_percentage": 84.5,
  "category_scores": {{
    "required_skills_match": 85.0,
    "project_relevance": 88.0,
    "education_relevance": 90.0,
    "experience_alignment": 78.0,
    "overall_jd_fit": 84.5
  }},
  "ai_screening_explanation": "Transparent breakdown of how the match score was calculated and recommended interview focus areas",
  "fairness_disclaimer": "Decision-Support Estimate Only: This screening analysis evaluates strictly job-related technical skills, projects, experience, and education. Protected attributes (gender, age, religion, caste, ethnicity, disability) are excluded. Final hiring decisions must be made by human recruiters."
}}
"""

FINAL_INTERVIEW_REPORT_PROMPT = """You are a Senior Engineering Hiring Committee Chair generating a comprehensive post-interview performance report.
Candidate Name: {candidate_name}
Domain: {domain} ({interview_type}, Difficulty: {difficulty}, Duration: {duration_minutes} mins)
Question & Answer Evaluation Records:
{qa_records}

Synthesize the entire session into an actionable final report and return ONLY valid JSON:
{{
  "overall_score": 8.4,
  "technical_knowledge": 8.5,
  "conceptual_understanding": 8.4,
  "problem_solving_ability": 8.2,
  "communication": 8.6,
  "grammar": 8.8,
  "answer_completeness": 8.1,
  "executive_summary": "Comprehensive paragraph evaluating overall interview readiness, depth of technical reasoning, and communication clarity",
  "strongest_topics": ["Topic 1", "Topic 2"],
  "weakest_topics": ["Topic needing review"],
  "skills_requiring_improvement": ["Skill 1", "Skill 2"],
  "suggested_learning_topics": ["Specific study module 1", "Study module 2", "Practice recommendation 3"],
  "recommended_next_difficulty": "Beginner | Intermediate | Advanced | Expert"
}}
"""
