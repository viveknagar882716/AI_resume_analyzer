# resume_parser.py (FIXED - Supports PDF & DOCX)
import re
import PyPDF2
from docx import Document  # ← NEW: For DOCX files
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILLS_DB = [
    "python", "java", "c++", "javascript", "sql", "mysql", "postgresql", "mongodb",
    "react", "angular", "vue", "node.js", "django", "flask", "spring", "html", "css",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "linux",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
    "pandas", "numpy", "scikit-learn", "matplotlib", "seaborn", "excel", "power bi", "tableau"
]

def extract_text_from_pdf(file_stream):
    """Extract text from PDF"""
    reader = PyPDF2.PdfReader(file_stream)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return clean_text(text)

def extract_text_from_docx(file_stream):
    """Extract text from DOCX"""
    try:
        doc = Document(file_stream)
        text = "\n".join([para.text for para in doc.paragraphs])
        return clean_text(text)
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII
    return text.strip().lower()

def compute_similarity(resume_text, job_desc):
    """Compute TF-IDF + Cosine Similarity"""
    if not resume_text.strip() or not job_desc.strip():
        raise Exception("Empty text provided for similarity calculation")
        
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_desc])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(similarity * 100, 2)

def extract_skills(text):
    """Extract skills from text"""
    found = []
    text_lower = text.lower()
    for skill in SKILLS_DB:
        if skill in text_lower:
            found.append(skill)
    return list(set(found))

def find_missing_skills(resume_skills, job_desc):
    """Find skills in job description that are missing in resume"""
    job_lower = job_desc.lower()
    missing = []
    for skill in SKILLS_DB:
        if skill in job_lower and skill not in resume_skills:
            missing.append(skill)
    return missing