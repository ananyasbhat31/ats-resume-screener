from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
import os
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Folder configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEMPLATES_FOLDER'] = os.path.join('static', 'template_files')
app.config['GENERATED_FOLDER'] = os.path.join('static', 'generated_resumes')

# Create folders if not exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['GENERATED_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Keyword extraction for ATS scoring
def extract_keywords(text):
    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = set(['the','and','to','a','in','of','for','on','with','at','by','an','be','is','are','as','that','this'])
    return set(w for w in words if w not in stopwords and len(w) > 2)

def ats_score(resume_text, job_desc_text):
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_desc_text)

    matched = resume_keywords.intersection(job_keywords)
    missing = job_keywords.difference(resume_keywords)

    score = int(len(matched) / len(job_keywords) * 100) if job_keywords else 0

    suggestions = []
    if score < 50:
        suggestions.append("Include key skills and experience from the job description.")
    elif score < 70:
        suggestions.append("Add more keywords from the job description.")
    else:
        suggestions.append("Great match! Just refine formatting for ATS.")

    return {
        'score': score,
        'matched_keywords': list(matched),
        'missing_keywords': list(missing),
        'improvement_suggestions': suggestions,
        'pro_tips': [
            "Use ATS-friendly formatting.",
            "Avoid using tables, graphics, or columns.",
            "Use standard headers like Experience, Skills, etc."
        ]
    }

# Home - ATS Resume Checker
@app.route('/', methods=['GET', 'POST'])
def home():
    results = None
    if request.method == 'POST':
        resume_file = request.files.get('resume')
        job_desc = request.form.get('job_description')

        if not resume_file or resume_file.filename == '':
            flash("Please upload your resume.")
            return redirect(request.url)

        if not job_desc or job_desc.strip() == '':
            flash("Please enter a job description.")
            return redirect(request.url)

        filename = secure_filename(resume_file.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume_file.save(resume_path)

        try:
            with open(resume_path, 'r', encoding='utf-8') as f:
                resume_text = f.read()
        except:
            flash("Only plain text (.txt) resumes are supported.")
            return redirect(request.url)

        results = ats_score(resume_text, job_desc)
        os.remove(resume_path)

    return render_template('home.html', results=results)

# Create Resume - Simple form
@app.route('/resume', methods=['GET', 'POST'])
def create_resume():
    if request.method == 'POST':
        data = request.form.to_dict()
        content = f"""
Name: {data.get('name')}
Email: {data.get('email')}
Phone: {data.get('phone')}

Summary:
{data.get('summary')}

Experience:
{data.get('experience')}

Education:
{data.get('education')}

Skills:
{data.get('skills')}
        """.strip()

        filename = secure_filename(f"{data.get('name', 'resume')}_resume.txt")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return send_file(filepath, as_attachment=True)

    return render_template('create_resume.html')

# Resume Templates
@app.route('/templates')
def templates():
    folder_path = app.config['TEMPLATES_FOLDER']
    templates_list = []

    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if file.endswith('.docx'):
                templates_list.append({
                    "filename": file,
                    "preview": file.replace('.docx', '.png')
                })

    return render_template('templates.html', templates=templates_list)

@app.route('/download_template/<filename>')
def download_template(filename):
    path = os.path.join(app.config['TEMPLATES_FOLDER'], filename)
    return send_file(path, as_attachment=True)

@app.route('/about')
def about():
    return render_template('about.html')

# ----------------------------
# Resume Builder (Multi-step)
# ----------------------------

@app.route('/resume-builder/step1', methods=['GET', 'POST'])
def step1():
    if request.method == 'POST':
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        session['phone'] = request.form['phone']
        return redirect(url_for('step2'))
    return render_template('step1.html')

@app.route('/resume-builder/step2', methods=['GET', 'POST'])
def step2():
    if request.method == 'POST':
        session['summary'] = request.form['summary']
        return redirect(url_for('step3'))
    return render_template('step2.html')

@app.route('/resume-builder/step3', methods=['GET', 'POST'])
def step3():
    if request.method == 'POST':
        session['experience'] = request.form['experience']
        return redirect(url_for('step4'))
    return render_template('step3.html')

@app.route('/resume-builder/step4', methods=['GET', 'POST'])
def step4():
    if request.method == 'POST':
        session['education'] = request.form['education']
        return redirect(url_for('step5'))
    return render_template('step4.html')

@app.route('/resume-builder/step5', methods=['GET', 'POST'])
def step5():
    if request.method == 'POST':
        session['skills'] = request.form['skills']
        return redirect(url_for('choose_template'))
    return render_template('step5.html')


@app.route('/resume-builder/choose-template', methods=['GET', 'POST'])
def choose_template():
    if request.method == 'POST':
        session['template'] = request.form['template']
        return redirect(url_for('preview_resume'))

    # Load template previews
    templates_list = []
    folder = app.config['TEMPLATES_FOLDER']
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.endswith('.docx'):
                templates_list.append({
                    "filename": f,
                    "preview": f.replace('.docx', '.png')
                })

    return render_template('choose_template.html', templates=templates_list)

@app.route('/resume-builder/preview', methods=['GET', 'POST'])
def preview_resume():
    data = dict(session)
    if request.method == 'POST':
        filename = secure_filename(f"{data.get('name', 'resume')}_resume.txt")
        filepath = os.path.join(app.config['GENERATED_FOLDER'], filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"""
Name: {data.get('name')}
Email: {data.get('email')}
Phone: {data.get('phone')}

Summary:
{data.get('summary')}

Experience:
{data.get('experience')}

Education:
{data.get('education')}

Skills:
{data.get('skills')}
            """.strip())

        return send_file(filepath, as_attachment=True)

    return render_template('preview.html', data=data)

@app.route('/download_resume', methods=['POST'])
def download_resume():
    data = request.form.to_dict()
    filename = secure_filename(f"{data.get('name')}_resume.txt")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    content = f"""
Name: {data.get('name')}
Email: {data.get('email')}
Phone: {data.get('phone')}

Summary:
{data.get('summary')}

Experience:
{data.get('experience')}

Education:
{data.get('education')}

Skills:
{data.get('skills')}
    """.strip()

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return send_file(filepath, as_attachment=True)

# ----------------------------

if __name__ == '__main__':
    app.run(debug=True)
