# 🤖 AI Resume Analyzer

An intelligent web app that analyzes your resume against a job description using NLP and provides a match score, skill gap analysis, and actionable suggestions.

## 🚀 Features

- Upload PDF or DOCX resumes
- Paste any job description
- Get a **match percentage** using TF-IDF + Cosine Similarity
- See **skills found** and **missing skills**
- Receive **personalized suggestions** to improve your resume
- Clean, responsive, and user-friendly UI

## 🧠 Tech Stack

- **Frontend**: Streamlit
- **Backend Logic**: Python
- **Libraries**: 
  - `PyPDF2`, `docx2txt` → Text extraction
  - `scikit-learn` → TF-IDF & Cosine Similarity
  - `re`, `nltk` (optional) → Text cleaning
- **Deployment**: Streamlit Cloud (free)

## ⚙️ How to Run Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/viveknagar882716/ai_resume_analyzer.git
   cd ai_resume_analyzer