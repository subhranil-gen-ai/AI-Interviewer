"""
Django -> FastAPI Service Communication Client (Layer 2 -> Layer 3)
Communicates with the independent FastAPI AI microservice via HTTP requests,
with automatic in-process fallback if the FastAPI worker port is unreachable.
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests

ROOT_PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_PROJECT_DIR))

from ai_service.resume_parser import extract_text_from_file
from ai_service.llm_engine import LLMServiceEngine

_fallback_engine = LLMServiceEngine()


def get_fastapi_base_url() -> str:
    return os.getenv("FASTAPI_SERVICE_URL", "http://127.0.0.1:8001").rstrip("/")


def call_fastapi_extract_resume(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    url = f"{get_fastapi_base_url()}/api/v1/resume/extract-file"
    try:
        files = {"file": (filename, file_bytes)}
        resp = requests.post(url, files=files, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 400:
            detail = resp.json().get("detail", "Invalid resume file.")
            raise ValueError(detail)
    except ValueError:
        raise
    except Exception:
        pass
    raw_text, _ = extract_text_from_file(file_bytes, filename)
    return _fallback_engine.extract_resume(raw_text)


def call_fastapi_analyze_resume(resume_text: str, extracted_data: Optional[Dict[str, Any]] = None, target_domain: str = "Software Engineering") -> Dict[str, Any]:
    url = f"{get_fastapi_base_url()}/api/v1/resume/analyze"
    payload = {
        "resume_text": resume_text,
        "extracted_data": extracted_data,
        "target_domain": target_domain,
    }
    try:
        resp = requests.post(url, json=payload, timeout=20)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return _fallback_engine.analyze_resume(resume_text, extracted_data, target_domain)


def call_fastapi_generate_question(payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{get_fastapi_base_url()}/api/v1/interview/generate-question"
    try:
        resp = requests.post(url, json=payload, timeout=20)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return _fallback_engine.generate_question(payload)


def call_fastapi_evaluate_answer(payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{get_fastapi_base_url()}/api/v1/interview/evaluate-answer"
    try:
        resp = requests.post(url, json=payload, timeout=20)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return _fallback_engine.evaluate_answer(payload)


def call_fastapi_adaptive_difficulty(current_difficulty: str, recent_scores: List[float], adaptive_enabled: bool = True) -> Dict[str, Any]:
    url = f"{get_fastapi_base_url()}/api/v1/interview/adaptive-difficulty"
    payload = {
        "current_difficulty": current_difficulty,
        "recent_scores": recent_scores,
        "adaptive_enabled": adaptive_enabled,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return _fallback_engine.compute_adaptive_difficulty(current_difficulty, recent_scores, adaptive_enabled)


def call_fastapi_screen_candidate(payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{get_fastapi_base_url()}/api/v1/screening/evaluate-candidate"
    try:
        resp = requests.post(url, json=payload, timeout=25)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return _fallback_engine.screen_candidate(payload)


def call_fastapi_final_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{get_fastapi_base_url()}/api/v1/interview/final-report"
    try:
        resp = requests.post(url, json=payload, timeout=25)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return _fallback_engine.generate_final_report(payload)
