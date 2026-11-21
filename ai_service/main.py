"""
FastAPI AI Processing Microservice (Layer 3)
Provides independent REST endpoints consumed by the Django backend:
- GET  /health
- POST /api/v1/resume/extract-file
- POST /api/v1/resume/analyze
- POST /api/v1/interview/generate-question
- POST /api/v1/interview/evaluate-answer
- POST /api/v1/interview/grammar-check
- POST /api/v1/interview/adaptive-difficulty
- POST /api/v1/screening/evaluate-candidate
- POST /api/v1/interview/final-report
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    ResumeExtractionResponse,
    ResumeAnalysisRequest,
    ResumeAnalysisResponse,
    QuestionGenerationRequest,
    QuestionGenerationResponse,
    AnswerEvaluationRequest,
    AnswerEvaluationResponse,
    GrammarAnalysisResult,
    AdaptiveDifficultyRequest,
    AdaptiveDifficultyResponse,
    CandidateScreeningRequest,
    CandidateScreeningResponse,
    FinalReportRequest,
    FinalReportResponse,
)
from .resume_parser import extract_text_from_file
from .llm_engine import LLMServiceEngine

app = FastAPI(
    title="AI Interviewer – FastAPI AI & NLP Microservice",
    description="Modular LLM, NLP Resume Intelligence, Dynamic Conversational Questioning, Semantic Evaluation & Ethical Candidate Screening Service.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = LLMServiceEngine()


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ai_interviewer_fastapi_service",
        "llm_provider_configured": engine.provider,
        "live_gemini_client_active": engine.gemini_client is not None,
    }


@app.post("/api/v1/resume/extract-file", response_model=ResumeExtractionResponse)
async def extract_resume_file(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        raw_text, _ = extract_text_from_file(file_bytes, file.filename or "resume.pdf")
        extracted = engine.extract_resume(raw_text)
        return ResumeExtractionResponse(**extracted)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Resume extraction error: {exc}") from exc


@app.post("/api/v1/resume/analyze", response_model=ResumeAnalysisResponse)
def analyze_resume_endpoint(payload: ResumeAnalysisRequest):
    result = engine.analyze_resume(
        resume_text=payload.resume_text,
        extracted_data=payload.extracted_data,
        target_domain=payload.target_domain or "Software Engineering",
    )
    return ResumeAnalysisResponse(**result)


@app.post("/api/v1/interview/generate-question", response_model=QuestionGenerationResponse)
def generate_interview_question(payload: QuestionGenerationRequest):
    result = engine.generate_question(payload.model_dump())
    return QuestionGenerationResponse(**result)


@app.post("/api/v1/interview/evaluate-answer", response_model=AnswerEvaluationResponse)
def evaluate_candidate_answer(payload: AnswerEvaluationRequest):
    result = engine.evaluate_answer(payload.model_dump())
    return AnswerEvaluationResponse(**result)


@app.post("/api/v1/interview/grammar-check", response_model=GrammarAnalysisResult)
def check_grammar_endpoint(payload: dict):
    answer_text = payload.get("candidate_answer", "")
    result = engine.analyze_grammar(answer_text)
    return GrammarAnalysisResult(**result)


@app.post("/api/v1/interview/adaptive-difficulty", response_model=AdaptiveDifficultyResponse)
def adaptive_difficulty_endpoint(payload: AdaptiveDifficultyRequest):
    result = engine.compute_adaptive_difficulty(
        current_difficulty=payload.current_difficulty,
        recent_scores=payload.recent_scores,
        adaptive_enabled=payload.adaptive_enabled,
    )
    return AdaptiveDifficultyResponse(**result)


@app.post("/api/v1/screening/evaluate-candidate", response_model=CandidateScreeningResponse)
def screen_candidate_endpoint(payload: CandidateScreeningRequest):
    result = engine.screen_candidate(payload.model_dump())
    return CandidateScreeningResponse(**result)


@app.post("/api/v1/interview/final-report", response_model=FinalReportResponse)
def generate_final_report_endpoint(payload: FinalReportRequest):
    result = engine.generate_final_report(payload.model_dump())
    return FinalReportResponse(**result)
