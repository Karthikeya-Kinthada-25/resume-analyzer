# Resume Analyzer

A minimal, AI-style resume analyzer website that scores resumes, extracts skills, compares them with job descriptions, checks ATS readiness, and generates stronger resume bullet suggestions.

## Features

- Smart skill extraction with contextual detection for ML, NLP, APIs, deployment, and AI-related terms
- Role-based optimization for Software Engineer, AI Engineer, Data Scientist, Data Analyst, Frontend Developer, Backend Developer, and Product Manager
- Resume score breakdown for skills, projects, experience, ATS compatibility, job match, and overall score
- Keyword gap analysis with present skills, missing skills, and high-priority skills
- Job description matching with match percentage and missing keywords
- ATS compatibility checks for links, measurable achievements, keyword density, formatting risks, and resume structure
- Resume improvement generator that rewrites weak project or achievement lines into stronger bullet points
- Voice feedback using browser speech synthesis
- System theme support with light/dark theme switch
- Minimal responsive dashboard with smooth animations

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python, Flask
- Resume parsing: PyPDF2, python-docx
- Deployment: GitHub + Vercel

## Project Structure

```text
resume-analyzer/
  api/
    index.py
  backend/
    app.py
    analyzer.py
    skills.py
    requirements.txt
  frontend/
    index.html
    style.css
    script.js
  requirements.txt
  vercel.json
  .gitignore
```

## Run Locally

Create and activate a virtual environment:

```powershell
cd C:\Users\karthikeya\PROJECTS\resume-analyzer
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Start the backend:

```powershell
cd C:\Users\karthikeya\PROJECTS\resume-analyzer\backend
C:\Users\karthikeya\PROJECTS\resume-analyzer\.venv\Scripts\python.exe app.py
```

Start the frontend in a second terminal:

```powershell
cd C:\Users\karthikeya\PROJECTS\resume-analyzer\frontend
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500
```

The backend runs at:

```text
http://127.0.0.1:5050
```

## Deploy With GitHub And Vercel

Upload these files and folders to GitHub:

- `api/`
- `backend/`
- `frontend/`
- `requirements.txt`
- `vercel.json`
- `.gitignore`
- `README.md`

Do not upload:

- `.venv/`
- `__pycache__/`
- `.pyc` files
- `.log` files

Deploy steps:

1. Create a new GitHub repository.
2. Push this project to GitHub.
3. Open Vercel and choose `Add New Project`.
4. Import your GitHub repository.
5. Keep the framework preset as `Other`.
6. Deploy.

The frontend will be served by Vercel, and API requests under `/api/...` will run through the Python Flask serverless entry in `api/index.py`.

## Notes

This project currently uses a rule-based AI-style analysis engine. It does not require an OpenAI or Gemini API key. Later, an LLM can be added to generate deeper personalized feedback and more advanced resume rewriting.

## LinkedIn Post Description

I built a Resume Analyzer web app that helps users improve their resumes for specific job roles.

It can analyze a resume, extract skills, calculate role-based scores, compare the resume with a job description, identify missing keywords, check ATS compatibility, and generate stronger bullet point suggestions.

Key features:

- Smart skill extraction
- Role-based resume optimization
- ATS compatibility checks
- Job description match scoring
- Keyword gap analysis
- Resume improvement generator
- Voice feedback
- Light/dark theme dashboard

Tech stack: HTML, CSS, JavaScript, Python, Flask, PyPDF2, python-docx, GitHub, and Vercel.

This project helped me understand how real resume screening tools combine text extraction, scoring logic, role-based keyword analysis, and clean dashboard UI design.

#WebDevelopment #Python #Flask #JavaScript #ResumeAnalyzer #ATS #Projects #OpenToWork #SoftwareDevelopment
