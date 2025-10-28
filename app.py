# app.py (with SQLite - FIXED VERSION)
import os
import sqlite3
from flask import Flask, request, jsonify, session, send_from_directory
from resume_parser import extract_text_from_pdf, compute_similarity,extract_text_from_docx, extract_skills, find_missing_skills
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__, static_folder='static')
# Use a strong secret key (critical for sessions)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Call on startup
init_db()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# Helper: get DB connection
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# ===== SIGN UP =====
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
        
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not all([name, email, password]):
        return jsonify({"error": "Name, email, and password required"}), 400
    
    # Basic validation
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
            (name, email, generate_password_hash(password))
        )
        conn.commit()
        session['user'] = email
        return jsonify({"message": "Account created!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409
    finally:
        conn.close()

# ===== SIGN IN =====
@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
        
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        session['user'] = email
        return jsonify({"message": "Signed in!"}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

# ===== ANALYSIS =====
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'user' not in session:
        return jsonify({"error": "Authentication required"}), 401

    if 'resume' not in request.files:
        return jsonify({"error": "Resume file required"}), 400

    resume_file = request.files['resume']
    if resume_file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    job_desc = request.form.get('jobDescription', '').strip()

    if not job_desc:
        return jsonify({"error": "Job description required"}), 400

    try:
        # Validate file type
        filename = resume_file.filename.lower()
        if not filename.endswith(('.pdf', '.docx')):
            return jsonify({"error": "Only PDF and DOCX files allowed"}), 400
            
        # Extract text based on file type
        if filename.endswith('.pdf'):
            resume_text = extract_text_from_pdf(resume_file)
        else:  # .docx
            resume_text = extract_text_from_docx(resume_file)
            
        if not resume_text.strip():
            return jsonify({"error": "Could not extract text from resume"}), 400
            
        similarity = compute_similarity(resume_text, job_desc)
        resume_skills = extract_skills(resume_text)
        missing_skills = find_missing_skills(resume_skills, job_desc)

        return jsonify({
            "match_score": similarity,
            "found_skills": resume_skills,
            "missing_skills": missing_skills
        })
    except Exception as e:
        app.logger.error(f"Analysis error: {str(e)}")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

# Serve static files (including images like pic.png)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=os.environ.get('FLASK_ENV') != 'production', host='0.0.0.0', port=port)