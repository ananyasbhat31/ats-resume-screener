import re
from sklearn.feature_extraction.text import CountVectorizer

TIPS = {
    "general": ["Keep resume within 1-2 pages.", "Use action verbs like 'developed', 'led', etc."],
    "resume_templates": [
        "https://www.resume.io/resume-templates",
        "https://resumegenius.com/resume-templates",
        "https://zety.com/resume-templates"
    ]
}

def score_resume(resume_text, job_description):
    resume_text = resume_text.lower()
    job_description = job_description.lower()

    resume_keywords = set(re.findall(r'\b\w+\b', resume_text))
    job_keywords = set(re.findall(r'\b\w+\b', job_description))

    matched_keywords = resume_keywords & job_keywords
    missing_keywords = job_keywords - resume_keywords

    score = int((len(matched_keywords) / len(job_keywords)) * 100)

    improvement_areas = list(missing_keywords)[:10]
    pro_tips = TIPS["general"]

    return {
        "score": score,
        "matched_keywords": list(matched_keywords),
        "missing_keywords": improvement_areas,
        "improvement_suggestions": improvement_areas,
        "pro_tips": pro_tips,
        "templates": TIPS["resume_templates"]
    }
