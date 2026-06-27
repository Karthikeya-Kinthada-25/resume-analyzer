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


This project helped me understand how real resume screening tools combine text extraction, scoring logic, role-based keyword analysis, and clean dashboard UI design.

#WebDevelopment #Python #Flask #JavaScript #ResumeAnalyzer #ATS #Projects #OpenToWork #SoftwareDevelopment
