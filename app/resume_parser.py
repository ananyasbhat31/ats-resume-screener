import docx2txt
import PyPDF2
import re
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
import spacy

nltk.download('stopwords')
nlp = spacy.load("en_core_web_sm")

def extract_text_from_resume(path):
    if path.endswith('.pdf'):
        with open(path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
            return text
    elif path.endswith('.docx'):
        return docx2txt.process(path)
    elif path.endswith('.txt'):
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    return ""

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\W+', ' ', text)
    return ' '.join([word for word in text.split() if word not in stopwords.words('english')])

def extract_keywords(text):
    doc = nlp(text)
    return list(set([chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text) > 2]))

def evaluate_resume(resume_path, job_description):
    resume_text = extract_text_from_resume(resume_path)
    cleaned_resume = clean_text(resume_text)
    cleaned_jd = clean_text(job_description)

    resume_keywords = set(extract_keywords(cleaned_resume))
    jd_keywords = set(extract_keywords(cleaned_jd))

    matched = resume_keywords & jd_keywords
    missing = jd_keywords - resume_keywords

    score = round((len(matched) / len(jd_keywords)) * 100, 2) if jd_keywords else 0

    suggestions = []
    if score < 50:
        suggestions.append("Include more keywords from the job description.")
    if 'team' not in cleaned_resume:
        suggestions.append("Mention your teamwork or collaboration skills.")
    if 'project' not in cleaned_resume:
        suggestions.append("Highlight any relevant projects.")

    pro_tips = [
        "Keep your resume concise and relevant to the job.",
        "Use job-specific keywords to pass ATS.",
        "Highlight measurable achievements.",
    ]

    templates = [
        "Modern ATS Template - clean and minimal",
        "Creative ATS Template - great for designers",
        "Professional Template - best for corporate roles"
    ]

    return {
        'score': score,
        'matched_keywords': ', '.join(matched),
        'missing_keywords': ', '.join(missing),
        'improvement_suggestions': suggestions,
        'pro_tips': pro_tips,
        'templates': templates
    }
