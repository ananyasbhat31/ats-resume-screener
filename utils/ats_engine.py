import re

def clean_text(text):
    return re.sub(r'[^A-Za-z0-9 ]+', '', text).lower()

def evaluate_resume(resume_text, job_description):
    resume_words = set(clean_text(resume_text).split())
    jd_words = set(clean_text(job_description).split())

    matched = resume_words & jd_words
    missing = jd_words - resume_words

    score = int((len(matched) / len(jd_words)) * 100) if jd_words else 0

    suggestions = []
    if score < 70:
        suggestions.append("Consider tailoring your resume to better match the job description.")
    if "experience" not in resume_words:
        suggestions.append("Add relevant work experience.")

    pro_tips = [
        "Keep your resume clean and ATS-friendly.",
        "Use standard headings like Education, Experience, Skills.",
        "Avoid graphics and tables.",
        "Use keywords from the job description."
    ]

    templates = [
        "Classic Chronological Template",
        "Modern Minimal Template",
        "ATS-Compliant Basic Template"
    ]

    return {
        "score": score,
        "matched_keywords": ', '.join(matched),
        "missing_keywords": ', '.join(missing),
        "improvement_suggestions": suggestions,
        "pro_tips": pro_tips,
        "templates": templates
    }
