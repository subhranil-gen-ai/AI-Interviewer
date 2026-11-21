from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class ResumeExtractionResponse(BaseModel):
    candidate_name: str = Field(default="")
    email: str = Field(default="")
    phone: str = Field(default="")
    education: List[str] = Field(default_factory=list)
    technical_skills: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    frameworks_libraries: List[str] = Field(default_factory=list)
    tools_technologies: List[str] = Field(default_factory=list)
    projects: List[Dict[str, str]] = Field(default_factory=list)
    internships: List[Dict[str, str]] = Field(default_factory=list)
    work_experience: List[Dict[str, str]] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    raw_text: str = Field(default="")


class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    extracted_data: Optional[Dict[str, Any]] = None
    target_domain: Optional[str] = "Software Engineering"


class ResumeAnalysisResponse(BaseModel):
    professional_summary: str
    technical_skill_summary: str
    strong_technical_areas: List[str]
    weak_or_missing_areas: List[str]
    project_analysis: List[Dict[str, str]]
    internship_analysis: List[str]
    education_summary: str
    suggested_interview_topics: List[str]
    resume_improvement_suggestions: List[str]
    readiness_score: int = Field(default=78, ge=0, le=100)


class QuestionGenerationRequest(BaseModel):
    domain: str
    subtopics: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    interview_type: str = "Technical Interview"
    difficulty: str = "Intermediate"
    resume_text: str = ""
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    previous_questions: List[str] = Field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    question_number: int = 1
    max_questions: int = 10
    duration_minutes: int = 15


class QuestionGenerationResponse(BaseModel):
    question_text: str
    question_category: str
    difficulty: str
    topic: str
    is_followup: bool = False
    follow_up_rationale: str = ""
    expected_key_concepts: List[str] = Field(default_factory=list)


class AnswerEvaluationRequest(BaseModel):
    question_text: str
    question_category: str = "Conceptual"
    difficulty: str = "Intermediate"
    domain: str = "Software Engineering"
    candidate_answer: str
    expected_key_concepts: List[str] = Field(default_factory=list)
    resume_context: str = ""


class GrammarAnalysisResult(BaseModel):
    original_answer: str
    corrected_answer: str
    grammar_score: float
    explanation_of_mistakes: List[str]
    communication_suggestions: List[str]


class AnswerEvaluationResponse(BaseModel):
    technical_correctness: float = Field(ge=0, le=10)
    relevance: float = Field(ge=0, le=10)
    conceptual_understanding: float = Field(ge=0, le=10)
    completeness: float = Field(ge=0, le=10)
    clarity: float = Field(ge=0, le=10)
    communication_quality: float = Field(ge=0, le=10)
    grammar: float = Field(ge=0, le=10)
    overall_score: float = Field(ge=0, le=10)
    weighting_formula: str
    overall_evaluation: str
    strengths: List[str]
    weaknesses: List[str]
    missing_concepts: List[str]
    incorrect_statements: List[str]
    improved_sample_answer: str
    suggestions_for_improvement: List[str]
    grammar_analysis: GrammarAnalysisResult
    answer_quality_tier: str  # "strong" | "excellent_practical" | "incomplete" | "incorrect" | "irrelevant"


class AdaptiveDifficultyRequest(BaseModel):
    current_difficulty: str
    recent_scores: List[float]
    adaptive_enabled: bool = True


class AdaptiveDifficultyResponse(BaseModel):
    previous_difficulty: str
    recommended_difficulty: str
    rolling_average: float
    adjustment_action: str  # "increased" | "maintained" | "reduced"
    rationale: str


class CandidateScreeningRequest(BaseModel):
    job_title: str
    job_description: str
    required_skills: List[str]
    preferred_qualifications: List[str] = Field(default_factory=list)
    minimum_experience_years: float = 0.0
    educational_requirements: str = ""
    resume_text: str
    extracted_resume: Optional[Dict[str, Any]] = None


class CandidateScreeningResponse(BaseModel):
    candidate_name: str
    resume_summary: str
    extracted_skills: List[str]
    matching_skills: List[str]
    missing_skills: List[str]
    relevant_projects: List[str]
    experience_summary: str
    education_relevance: str
    internship_evaluation: str
    certifications_evaluation: str
    strengths: List[str]
    potential_skill_gaps: List[str]
    job_match_percentage: float = Field(ge=0, le=100)
    category_scores: Dict[str, float]
    ai_screening_explanation: str
    fairness_disclaimer: str


class FinalReportRequest(BaseModel):
    candidate_name: str
    domain: str
    interview_type: str
    difficulty: str
    duration_minutes: int
    qa_records: List[Dict[str, Any]]


class FinalReportResponse(BaseModel):
    overall_score: float
    technical_knowledge: float
    conceptual_understanding: float
    problem_solving_ability: float
    communication: float
    grammar: float
    answer_completeness: float
    executive_summary: str
    strongest_topics: List[str]
    weakest_topics: List[str]
    skills_requiring_improvement: List[str]
    suggested_learning_topics: List[str]
    recommended_next_difficulty: str
