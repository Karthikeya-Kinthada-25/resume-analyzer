import os
import tempfile

from docx import Document
from flask import Flask, jsonify, request
from flask_cors import CORS
from PyPDF2 import PdfReader

from analyzer import generate_improvements, score_resume
from skills import ROLE_SKILLS


app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024


def extract_text_from_pdf(path):
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)


def extract_text(file_storage):
    filename = (file_storage.filename or "").lower()
    suffix = os.path.splitext(filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        file_storage.save(temp_file.name)
        temp_path = temp_file.name
    try:
        if suffix == ".pdf":
            return extract_text_from_pdf(temp_path)
        if suffix == ".docx":
            return extract_text_from_docx(temp_path)
        if suffix in {".txt", ".md"}:
            with open(temp_path, "r", encoding="utf-8", errors="ignore") as handle:
                return handle.read()
        raise ValueError("Unsupported file type. Upload PDF, DOCX, TXT, or MD.")
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/roles")
def roles():
    return jsonify(
        [
            {"id": role_id, "label": details["label"], "required": details["required"], "advanced": details["advanced"]}
            for role_id, details in ROLE_SKILLS.items()
        ]
    )


@app.post("/api/analyze")
def analyze():
    resume_text = request.form.get("resumeText", "")
    target_role = request.form.get("targetRole", "software-engineer")
    job_description = request.form.get("jobDescription", "")

    uploaded_file = request.files.get("resume")
    if uploaded_file and uploaded_file.filename:
        resume_text = extract_text(uploaded_file)

    if not resume_text.strip():
        return jsonify({"error": "Upload a resume file or paste resume text."}), 400

    result = score_resume(resume_text, target_role, job_description)
    return jsonify(result)


@app.post("/api/improve")
def improve():
    resume_text = request.form.get("resumeText", "")
    uploaded_file = request.files.get("resume")
    if uploaded_file and uploaded_file.filename:
        resume_text = extract_text(uploaded_file)
    if not resume_text.strip():
        return jsonify({"error": "Upload a resume file or paste resume text."}), 400
    analysis = score_resume(resume_text, request.form.get("targetRole", "software-engineer"), request.form.get("jobDescription", ""))
    return jsonify({"improvements": generate_improvements(resume_text, analysis["skills"]["found"])})


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5050)
