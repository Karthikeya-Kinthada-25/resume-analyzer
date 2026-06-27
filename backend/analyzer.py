import re
from collections import Counter

from skills import ACTION_VERBS, CONTEXT_PATTERNS, GLOBAL_SKILLS, ROLE_SKILLS, SECTION_KEYWORDS


EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?:(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4})")
URL_RE = re.compile(r"(https?://\S+|linkedin\.com/\S+|github\.com/\S+)", re.I)
METRIC_RE = re.compile(r"(\d+%|\$\d+|\d+\s?(?:x|k|m|users|clients|projects|seconds|hours|days))", re.I)


def normalize(text):
    return re.sub(r"\s+", " ", text or "").strip()


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, round(value)))


def contains_phrase(text, phrase):
    phrase = phrase.lower()
    if len(phrase) <= 3 or any(char in phrase for char in "+#"):
        return phrase in text
    return re.search(rf"\b{re.escape(phrase)}\b", text) is not None


def extract_skills(text):
    lowered = text.lower()
    skills = {skill for skill in GLOBAL_SKILLS if contains_phrase(lowered, skill)}
    for skill, patterns in CONTEXT_PATTERNS.items():
        if any(re.search(pattern, lowered) for pattern in patterns):
            skills.add(skill)
    if "python" in skills and any(skill in skills for skill in {"machine learning", "deep learning", "nlp", "computer vision"}):
        skills.add("ai")
    return sorted(skills)


def extract_projects(text):
    raw_lines = text.splitlines()
    if len(raw_lines) <= 2:
        raw_lines = re.split(r"(?<=[.!?])\s+|(?:\s+-\s+)", text)
    lines = [line.strip(" -•\t") for line in raw_lines if line.strip()]
    project_lines = [
        line
        for line in lines
        if re.search(r"\b(project|built|developed|created|designed|implemented|model|app|dashboard|system)\b", line, re.I)
    ]
    return project_lines[:8]


def improve_bullet(line, found_skills):
    cleaned = re.sub(r"\s+", " ", line.strip(" -•\t")).strip(".")
    if not cleaned:
        return ""
    if cleaned.lower().startswith("did "):
        cleaned = cleaned[4:]
    if re.search(r"\b(developed|built|implemented|designed|optimized|automated|created|analyzed|led)\b", cleaned, re.I):
        starter = cleaned[0].upper() + cleaned[1:]
    else:
        starter = f"Developed {cleaned}"
    if not METRIC_RE.search(starter):
        starter += " with measurable improvements in quality, speed, or user impact"
    suggested_skills = readable_skill_list(found_skills)
    skill_tail = ", ".join(suggested_skills[:3])
    if skill_tail and not any(skill.lower() in starter.lower() for skill in suggested_skills[:3]):
        starter += f" using {skill_tail}"
    return starter.rstrip(".") + "."


def readable_skill_list(found_skills):
    labels = {
        "ai": "AI",
        "ml": "machine learning",
        "api": "APIs",
        "nlp": "NLP",
        "llm": "LLMs",
        "sql": "SQL",
        "rag": "RAG",
    }
    readable = []
    for skill in found_skills:
        label = labels.get(skill, skill)
        if label not in readable:
            readable.append(label)
    if "machine learning" in readable and "AI" in readable:
        readable.remove("AI")
    return readable


def generate_improvements(text, found_skills):
    source_lines = extract_projects(text)
    if not source_lines:
        source_lines = [
            "Built a project related to the target role",
            "Worked on data analysis and problem solving",
            "Created a technical solution for users",
        ]
    return [
        {"before": line, "after": improve_bullet(line, found_skills)}
        for line in source_lines[:5]
    ]


def detect_sections(text):
    lowered = text.lower()
    detected = {}
    for section, keywords in SECTION_KEYWORDS.items():
        detected[section] = any(re.search(rf"(^|\n|\s){re.escape(keyword)}(\s|:|\n|$)", lowered) for keyword in keywords)
    return detected


def infer_level(score, years_count, project_count):
    if score >= 82 and (years_count >= 3 or project_count >= 4):
        return "Advanced"
    if score >= 62:
        return "Intermediate"
    if score >= 42:
        return "Entry level"
    return "Needs major improvement"


def score_resume(text, target_role, job_description=""):
    clean_text = normalize(text)
    lowered = clean_text.lower()
    words = re.findall(r"[a-zA-Z][a-zA-Z+#.-]*", clean_text)
    word_count = len(words)
    sections = detect_sections(text)
    found_skills = extract_skills(clean_text)
    role = ROLE_SKILLS.get(target_role, ROLE_SKILLS["software-engineer"])
    required = role["required"]
    advanced = role["advanced"]
    present_required = [skill for skill in required if skill in found_skills or contains_phrase(lowered, skill)]
    missing_required = [skill for skill in required if skill not in present_required]
    present_advanced = [skill for skill in advanced if skill in found_skills or contains_phrase(lowered, skill)]
    job_keywords = extract_job_keywords(job_description)
    matched_job_keywords = [keyword for keyword in job_keywords if contains_phrase(lowered, keyword)]
    missing_job_keywords = [keyword for keyword in job_keywords if keyword not in matched_job_keywords][:12]

    contact_score = 0
    contact_items = {
        "email": bool(EMAIL_RE.search(clean_text)),
        "phone": bool(PHONE_RE.search(clean_text)),
        "links": bool(URL_RE.search(clean_text)),
    }
    contact_score += 35 if contact_items["email"] else 0
    contact_score += 30 if contact_items["phone"] else 0
    contact_score += 35 if contact_items["links"] else 0

    section_score = sum(sections.values()) / len(sections) * 100
    skills_score = (len(present_required) / len(required)) * 78 + min(len(present_advanced) * 7, 22)
    metrics_count = len(METRIC_RE.findall(clean_text))
    action_count = sum(1 for verb in ACTION_VERBS if contains_phrase(lowered, verb))
    impact_score = clamp(min(metrics_count * 12, 55) + min(action_count * 5, 45))
    length_score = clamp(100 - abs(520 - word_count) / 6) if word_count else 0
    ats_score = calculate_ats_score(clean_text, sections, found_skills)
    jd_score = 100 if not job_keywords else (len(matched_job_keywords) / len(job_keywords)) * 100
    project_count = len(extract_projects(text))
    project_score = clamp((35 if sections.get("projects") else 0) + min(project_count * 13, 40) + min(metrics_count * 7, 25))
    experience_score = clamp((35 if sections.get("experience") else 0) + min(action_count * 7, 35) + min(metrics_count * 8, 30))

    overall = clamp(
        contact_score * 0.12
        + section_score * 0.18
        + skills_score * 0.24
        + impact_score * 0.18
        + ats_score * 0.16
        + jd_score * 0.12
    )

    recommendations = build_recommendations(
        contact_items,
        sections,
        word_count,
        missing_required,
        missing_job_keywords,
        metrics_count,
        action_count,
    )

    return {
        "overallScore": overall,
        "level": infer_level(overall, len(re.findall(r"\b\d+\+?\s+years?\b", lowered)), lowered.count("project")),
        "targetRole": role["label"],
        "wordCount": word_count,
        "sectionScores": {
            "Skills Score": clamp(skills_score),
            "Projects Score": clamp(project_score),
            "Experience Score": clamp(experience_score),
            "ATS Score": clamp(ats_score),
            "Job Match": clamp(jd_score),
            "Overall Score": overall,
        },
        "detailScores": {
            "Contact": clamp(contact_score),
            "Resume Structure": clamp(section_score),
            "Impact Evidence": clamp(impact_score),
            "Length Balance": clamp(length_score),
        },
        "sections": sections,
        "contact": contact_items,
        "skills": {
            "found": found_skills,
            "matchedRequired": present_required,
            "missingRequired": missing_required,
            "matchedAdvanced": present_advanced,
            "suggestedAdvanced": [skill for skill in advanced if skill not in present_advanced],
            "highPriority": missing_required[:4] + [skill for skill in missing_job_keywords if skill in required][:3],
        },
        "jobMatch": {
            "keywordsUsed": job_keywords,
            "matched": matched_job_keywords,
            "missing": missing_job_keywords,
        },
        "signals": {
            "metricsCount": metrics_count,
            "actionVerbCount": action_count,
            "atsWarnings": ats_warnings(clean_text),
            "keywordDensity": calculate_keyword_density(clean_text, found_skills),
        },
        "charts": {
            "skillDistribution": skill_distribution(found_skills),
        },
        "improvements": generate_improvements(text, found_skills),
        "recommendations": recommendations,
        "voiceSummary": build_voice_summary(overall, role["label"], missing_required, missing_job_keywords, ats_warnings(clean_text)),
    }


def calculate_ats_score(text, sections, found_skills):
    score = 55
    if len(text) > 1200:
        score += 10
    if sections.get("experience"):
        score += 8
    if sections.get("skills"):
        score += 8
    if len(found_skills) >= 8:
        score += 10
    if "table" in text.lower() or "image" in text.lower():
        score -= 8
    if not EMAIL_RE.search(text):
        score -= 6
    return clamp(score)


def ats_warnings(text):
    lowered = text.lower()
    warnings = []
    if "references available" in lowered:
        warnings.append("Remove references line and use the space for measurable achievements.")
    if len(text) < 1200:
        warnings.append("Resume text is short; add more role-specific evidence if your experience allows it.")
    if not URL_RE.search(text):
        warnings.append("Add LinkedIn, GitHub, portfolio, or a relevant professional link.")
    if len(METRIC_RE.findall(text)) < 3:
        warnings.append("Add more numbers such as percentages, scale, revenue, users, or time saved.")
    if "table" in lowered or "image" in lowered:
        warnings.append("Avoid tables, images, and graphics that many ATS systems cannot parse reliably.")
    return warnings


def calculate_keyword_density(text, found_skills):
    word_count = max(1, len(re.findall(r"\w+", text)))
    return round((len(found_skills) / word_count) * 100, 2)


def skill_distribution(found_skills):
    groups = {
        "Programming": {"python", "javascript", "typescript", "java", "c++", "c#", "sql"},
        "AI/Data": {"machine learning", "deep learning", "nlp", "ai", "ml", "pandas", "numpy", "tensorflow", "pytorch", "llm"},
        "Web/Cloud": {"react", "node", "api", "rest api", "docker", "aws", "azure", "gcp", "kubernetes"},
        "Product/Soft": {"leadership", "communication", "stakeholder", "roadmap", "agile", "problem solving"},
    }
    return {
        label: sum(1 for skill in found_skills if skill in values)
        for label, values in groups.items()
    }


def extract_job_keywords(job_description):
    if not job_description:
        return []
    lowered = job_description.lower()
    known = [skill for skill in GLOBAL_SKILLS if contains_phrase(lowered, skill)]
    words = re.findall(r"\b[a-z][a-z+#.-]{3,}\b", lowered)
    stop_words = {
        "with",
        "from",
        "that",
        "this",
        "your",
        "will",
        "have",
        "work",
        "team",
        "role",
        "using",
        "and",
        "the",
        "for",
        "are",
        "you",
        "need",
        "needs",
        "required",
        "candidate",
        "experience",
        "years",
        "responsibilities",
        "qualifications",
    }
    frequent = [word for word, _ in Counter(word for word in words if word not in stop_words).most_common(12)]
    return sorted(set(known + frequent))[:18]


def build_recommendations(contact, sections, word_count, missing_required, missing_job_keywords, metrics_count, action_count):
    recommendations = []
    if not all(contact.values()):
        recommendations.append("Make contact details complete: email, phone, and one professional link.")
    missing_sections = [name.title() for name, present in sections.items() if not present]
    if missing_sections:
        recommendations.append(f"Add or clearly label these sections: {', '.join(missing_sections[:4])}.")
    if word_count < 350:
        recommendations.append("Expand bullets with scope, tools used, and outcomes; the resume is currently light.")
    elif word_count > 900:
        recommendations.append("Trim older or repeated details so recruiters can scan the strongest evidence quickly.")
    if missing_required:
        recommendations.append(f"Prioritize these role skills: {', '.join(missing_required[:6])}.")
        if {"deep learning", "nlp", "llm"} & set(missing_required):
            recommendations.append("For AI Engineer roles, add NLP, deep learning, or LLM projects with clear model results.")
    if missing_job_keywords:
        recommendations.append(f"Mirror important job-description language where truthful: {', '.join(missing_job_keywords[:6])}.")
    if metrics_count < 3:
        recommendations.append("Rewrite bullets to include measurable impact, such as percentage improvement or users served.")
    if action_count < 6:
        recommendations.append("Start more bullets with strong action verbs like built, optimized, automated, led, or delivered.")
    if not recommendations:
        recommendations.append("Resume is in solid shape; focus next on tailoring the top half for each job posting.")
    return recommendations


def build_voice_summary(score, role_label, missing_required, missing_job_keywords, ats_warning_list):
    gaps = missing_required[:3] or missing_job_keywords[:3]
    gap_text = ", ".join(gaps) if gaps else "no major required skill gaps"
    ats_text = ats_warning_list[0] if ats_warning_list else "ATS compatibility looks acceptable."
    return f"Your resume score is {score} for {role_label}. Main focus areas: {gap_text}. {ats_text}"
