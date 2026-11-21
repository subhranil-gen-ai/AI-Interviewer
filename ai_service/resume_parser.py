"""
Resume Document Parsing & NLP Extraction Module (Module 3)
Supports:
- PDF files (via pdfplumber with pypdf fallback)
- DOCX files (via python-docx)
- TXT / Markdown fallback
- Legacy .DOC limitation detection with clear explanation
- Rule-based + NLP entity/skill/project extraction supporting LLM enrichment
"""
import io
import re
from typing import Dict, List, Any, Tuple

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import docx
except ImportError:
    docx = None


KNOWN_PROGRAMMING_LANGUAGES = [
    "Python", "Java", "C++", "C", "C#", "JavaScript", "TypeScript", "SQL",
    "Go", "Rust", "Kotlin", "Swift", "PHP", "Ruby", "R", "MATLAB", "Bash", "HTML5", "CSS3"
]

KNOWN_FRAMEWORKS_LIBRARIES = [
    "Django", "FastAPI", "Flask", "React", "Angular", "Vue.js", "Node.js", "Express",
    "Spring Boot", "Scikit-learn", "TensorFlow", "PyTorch", "Keras", "Random Forest",
    "XGBoost", "LightGBM", "Pandas", "NumPy", "SciPy", "NLTK", "spaCy", "OpenCV",
    "Sentence Transformers", "Hugging Face", "LangChain", "Bootstrap", "Tailwind CSS",
    "Chart.js", "REST API", "GraphQL", "Microservices"
]

KNOWN_TOOLS_TECHNOLOGIES = [
    "Git", "GitHub", "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Linux",
    "SQLite", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Jenkins", "CI/CD",
    "Google Colab", "Jupyter", "Postman", "Nginx", "Celery", "Jira"
]

KNOWN_DOMAINS_CONCEPTS = [
    "Machine Learning", "Deep Learning", "Natural Language Processing", "Generative AI",
    "Data Science", "Data Analytics", "Data Structures and Algorithms", "Operating Systems",
    "Computer Networks", "DBMS", "Object-Oriented Programming", "System Design",
    "Cybersecurity", "Cloud Computing", "DevOps", "Full Stack Development",
    "Class Imbalance", "SMOTE", "Feature Engineering", "Model Deployment"
]


def extract_text_from_file(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    """
    Extracts plain text from uploaded resume bytes (.pdf, .docx, .txt).
    Returns (extracted_text, status_message).
    Raises ValueError for unsupported legacy binary .doc or corrupted files.
    """
    lower_name = (filename or "").lower().strip()
    if not file_bytes:
        raise ValueError("Uploaded file is empty (0 bytes).")
    if len(file_bytes) > 10 * 1024 * 1024:
        raise ValueError("File exceeds maximum allowed size of 10 MB.")

    if lower_name.endswith(".doc") and not lower_name.endswith(".docx"):
        # Check if it's actually plain text or RTF masquerading as .doc
        try:
            text_attempt = file_bytes.decode("utf-8")
            if len(text_attempt.strip()) > 30:
                return text_attempt.strip(), "Extracted text from UTF-8 .doc file."
        except UnicodeDecodeError:
            pass
        raise ValueError(
            "Legacy binary Microsoft Word (.doc, 97-2003) format detected. "
            "Standard open-source Python extraction libraries (pdfplumber/python-docx) "
            "require modern .pdf or .docx formats without external OS binary converters. "
            "Please save or export your resume as a PDF (.pdf) or Word (.docx) file and re-upload."
        )

    if lower_name.endswith(".pdf"):
        extracted_pages = []
        if pdfplumber is not None:
            try:
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    for page in pdf.pages:
                        page_txt = page.extract_text() or ""
                        if page_txt.strip():
                            extracted_pages.append(page_txt)
            except Exception:
                pass
        if not extracted_pages and pypdf is not None:
            try:
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                for page in reader.pages:
                    page_txt = page.extract_text() or ""
                    if page_txt.strip():
                        extracted_pages.append(page_txt)
            except Exception as exc:
                raise ValueError(f"Unable to parse PDF file: {exc}") from exc
        full_text = "\n".join(extracted_pages).strip()
        if not full_text:
            raise ValueError("No readable text found in PDF. Ensure the PDF contains selectable text rather than scanned images.")
        return full_text, "Successfully extracted text from PDF via pdfplumber/pypdf."

    if lower_name.endswith(".docx"):
        if docx is None:
            raise ValueError("python-docx library is not installed.")
        try:
            document = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
            # Also extract text from tables in the DOCX resume
            for table in document.tables:
                for row in table.rows:
                    row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_cells:
                        paragraphs.append(" | ".join(dict.fromkeys(row_cells)))
            full_text = "\n".join(paragraphs).strip()
            if not full_text:
                raise ValueError("The uploaded DOCX document contains no readable text.")
            return full_text, "Successfully extracted text from DOCX via python-docx."
        except Exception as exc:
            raise ValueError(f"Unable to parse DOCX file: {exc}") from exc

    if lower_name.endswith((".txt", ".md")):
        return file_bytes.decode("utf-8", errors="replace").strip(), "Extracted text from plain text file."

    raise ValueError("Unsupported file format. Please upload a PDF (.pdf) or Word (.docx) file.")


def _match_keywords(text: str, candidates: List[str]) -> List[str]:
    found = []
    for item in candidates:
        pattern = r"(?<![A-Za-z0-9])" + re.escape(item) + r"(?![A-Za-z0-9])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(item)
    return found


def parse_resume_entities_nlp(resume_text: str) -> Dict[str, Any]:
    """
    Deterministic NLP parser that extracts candidate name, email, phone, education,
    categorized skills, projects, internships, work experience, and certifications.
    Used both as pre-extraction grounding for the LLM and as a fast fallback.
    """
    lines = [ln.strip() for ln in resume_text.splitlines() if ln.strip()]

    # 1. Email & Phone
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", resume_text)
    email = email_match.group(0) if email_match else ""

    phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3,5}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{4,6}", resume_text)
    phone = phone_match.group(0).strip() if phone_match else ""

    # 2. Candidate Name heuristic (first non-header line that isn't an email/URL)
    candidate_name = "Candidate"
    skip_headers = {"resume", "curriculum vitae", "cv", "profile", "contact", "summary"}
    for ln in lines[:6]:
        clean = re.sub(r"[^A-Za-z\s.]", "", ln).strip()
        if (
            2 <= len(clean.split()) <= 5
            and clean.lower() not in skip_headers
            and "@" not in ln
            and "http" not in ln.lower()
        ):
            candidate_name = clean.title()
            break

    # 3. Skills categorization
    prog_langs = _match_keywords(resume_text, KNOWN_PROGRAMMING_LANGUAGES)
    frameworks = _match_keywords(resume_text, KNOWN_FRAMEWORKS_LIBRARIES)
    tools = _match_keywords(resume_text, KNOWN_TOOLS_TECHNOLOGIES)
    concepts = _match_keywords(resume_text, KNOWN_DOMAINS_CONCEPTS)

    all_skills = list(dict.fromkeys(prog_langs + frameworks + tools + concepts))

    # 4. Section segmentation
    section_headers = {
        "education": re.compile(r"^(education|academic|qualifications|academics)\b", re.I),
        "projects": re.compile(r"^(projects|academic projects|technical projects|key projects)\b", re.I),
        "internships": re.compile(r"^(internships?|industrial training|summer internship)\b", re.I),
        "experience": re.compile(r"^(work experience|experience|employment|professional experience)\b", re.I),
        "certifications": re.compile(r"^(certifications?|courses|achievements|certificates)\b", re.I),
        "skills": re.compile(r"^(technical skills|skills|core competencies|technologies)\b", re.I),
    }

    sections: Dict[str, List[str]] = {k: [] for k in section_headers}
    current_sec = None
    for ln in lines:
        cleaned_header = re.sub(r"[:\-|#*]+", "", ln).strip()
        matched_sec = None
        if len(cleaned_header.split()) <= 4:
            for sec_name, regex in section_headers.items():
                if regex.search(cleaned_header):
                    matched_sec = sec_name
                    break
        if matched_sec:
            current_sec = matched_sec
            continue
        if current_sec:
            sections[current_sec].append(ln)

    # Fallback education extraction if section header wasn't isolated
    education = sections["education"][:4]
    if not education:
        edu_regex = re.compile(r"(B\.?Tech|M\.?Tech|B\.?E|B\.?Sc|M\.?Sc|MCA|BCA|Computer Science|Engineering|University|College|CGPA|GPA)", re.I)
        education = [ln for ln in lines if edu_regex.search(ln)][:3]

    # Projects extraction
    projects: List[Dict[str, str]] = []
    raw_proj_lines = sections["projects"]
    if raw_proj_lines:
        curr_title = None
        curr_desc = []
        for ln in raw_proj_lines:
            is_bullet = ln.startswith(("-", "*", "•", "–"))
            if not is_bullet and (len(ln.split()) <= 10 or "|" in ln or ":" in ln):
                if curr_title:
                    joined_desc = " ".join(curr_desc) if curr_desc else curr_title
                    techs = ", ".join(_match_keywords(curr_title + " " + joined_desc, all_skills)) or "Python, Software Engineering"
                    projects.append({
                        "title": curr_title.lstrip("-*• "),
                        "technologies": techs,
                        "description": joined_desc,
                    })
                curr_title = ln.split("|")[0].split("–")[0].strip()
                curr_desc = [ln]
            else:
                if not curr_title:
                    curr_title = ln.lstrip("-*• ")[:65]
                curr_desc.append(ln.lstrip("-*• "))
        if curr_title:
            joined_desc = " ".join(curr_desc)
            techs = ", ".join(_match_keywords(curr_title + " " + joined_desc, all_skills)) or "Python"
            projects.append({
                "title": curr_title.lstrip("-*• "),
                "technologies": techs,
                "description": joined_desc,
            })

    # Also scan full text for specific named projects if section parsing missed them
    if not projects:
        proj_matches = re.findall(r"([A-Z][A-Za-z0-9\s\-/]+(?:Project|System|Platform|Detection|Prediction|Application|Portal|Engine))", resume_text)
        for pm in list(dict.fromkeys(proj_matches))[:3]:
            title = pm.strip()
            if len(title.split()) >= 2:
                techs = ", ".join(_match_keywords(resume_text, all_skills)[:5]) or "Python"
                projects.append({
                    "title": title,
                    "technologies": techs,
                    "description": f"Developed {title} utilizing {techs}.",
                })

    # Internships
    internships: List[Dict[str, str]] = []
    for ln in sections["internships"][:4]:
        internships.append({
            "role": "Technical Intern",
            "company": ln[:80],
            "duration": "Completed",
            "summary": ln,
        })

    # Work Experience
    work_experience: List[Dict[str, str]] = []
    for ln in sections["experience"][:4]:
        work_experience.append({
            "role": "Software / AI Engineer",
            "company": ln[:80],
            "duration": "Experience Record",
            "summary": ln,
        })

    certifications = [ln.lstrip("-*• ") for ln in sections["certifications"][:5]]

    return {
        "candidate_name": candidate_name,
        "email": email,
        "phone": phone,
        "education": education or ["B.Tech in Computer Science and Engineering"],
        "technical_skills": all_skills or ["Python", "Data Structures", "SQL", "Software Engineering"],
        "programming_languages": prog_langs or ["Python"],
        "frameworks_libraries": frameworks,
        "tools_technologies": tools,
        "projects": projects,
        "internships": internships,
        "work_experience": work_experience,
        "certifications": certifications,
        "raw_text": resume_text,
    }
