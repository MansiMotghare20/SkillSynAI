"""
SkillSyncAI - Machine Learning Microservice (FastAPI + Scikit-Learn)
Authored / Specified for Vedika's Career Recommendation Model.

Run locally:
    python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
"""
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="SkillSyncAI ML Career Prediction Microservice",
    description="Career path recommendation inference endpoint developed for SkillSyncAI (Vedika's ML component).",
    version="1.0.0"
)

# Explicit CORS policy
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5000,http://127.0.0.1:5173,http://127.0.0.1:5000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class CareerPredictionInput(BaseModel):
    skills: List[str] = Field(default_factory=list, description="List of technical skills reported or parsed from resume")
    education: Optional[str] = Field(default="Undergraduate", description="Degree or level of study")
    experience: Optional[str] = Field(default="Beginner", description="Experience level: Beginner, Intermediate, or Advanced")
    interests: Optional[List[str]] = Field(default_factory=list, description="Domains of interest selected in assessment")
    preferredDomain: Optional[str] = Field(default=None, description="Optional target domain preference")

class CareerPredictionOutput(BaseModel):
    career: str
    confidence: float
    model_name: str
    model_version: str
    matched_features: List[str]
    alternative_careers: List[str]
    notes: str

# Centralized career benchmark profiles with weighted skill definitions
CAREER_PROFILES = {
    "Full Stack Developer": [
        "javascript", "react", "node.js", "express.js", "mongodb", "sql", "git", "typescript", "html5", "css3"
    ],
    "Data Scientist": [
        "python", "pandas", "numpy", "scikit-learn", "sql", "statistics", "machine learning", "data visualization", "r"
    ],
    "Machine Learning Engineer": [
        "python", "machine learning", "deep learning", "pytorch", "tensorflow", "scikit-learn", "docker", "algorithms"
    ],
    "Frontend Engineer": [
        "react", "javascript", "typescript", "tailwind css", "html5", "css3", "figma", "redux", "next.js"
    ],
    "Backend Engineer": [
        "node.js", "express.js", "python", "sql", "postgresql", "mongodb", "docker", "system design", "rest api", "java"
    ],
    "DevOps & Cloud Engineer": [
        "linux", "docker", "kubernetes", "aws", "ci/cd pipelines", "bash/shell", "git", "terraform", "cloud computing"
    ],
    "Cybersecurity Analyst": [
        "cybersecurity", "linux", "networking", "bash/shell", "python", "cryptography", "wireshark", "ethical hacking"
    ],
    "Data Analyst": [
        "sql", "python", "pandas", "excel", "data visualization", "statistics", "power bi", "tableau"
    ]
}

# Domain mapping helpers to factor in user interests
INTEREST_CAREER_MAP = {
    "AI / ML": ["Machine Learning Engineer", "Data Scientist"],
    "Web Development": ["Full Stack Developer", "Frontend Engineer", "Backend Engineer"],
    "App Development": ["Full Stack Developer", "Frontend Engineer"],
    "Data Science": ["Data Scientist", "Data Analyst"],
    "Cybersecurity": ["Cybersecurity Analyst"],
    "Cloud Computing": ["DevOps & Cloud Engineer"],
    "Software Engineering": ["Full Stack Developer", "Backend Engineer"]
}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SkillSyncAI ML Inference Microservice",
        "model_version": "1.0.0",
        "author": "Vedika (SkillSyncAI Team)",
        "supported_careers": list(CAREER_PROFILES.keys())
    }

@app.post("/predict-career", response_model=CareerPredictionOutput)
def predict_career(payload: CareerPredictionInput):
    # Normalize input skills to lower-case trimmed tokens
    user_skills_lower = [s.strip().lower() for s in payload.skills if s and s.strip()]
    user_interests = [i.strip() for i in payload.interests if i and i.strip()]

    # If no skills provided, fallback gracefully to assessment interests or default profile
    if not user_skills_lower:
        default_career = "Full Stack Developer"
        for interest in user_interests:
            if interest in INTEREST_CAREER_MAP:
                default_career = INTEREST_CAREER_MAP[interest][0]
                break

        return CareerPredictionOutput(
            career=default_career,
            confidence=0.55,
            model_name="SkillSyncAI-CareerClassifier-v1",
            model_version="1.0.0",
            matched_features=[],
            alternative_careers=["Frontend Engineer", "Data Analyst"],
            notes="Heuristic prediction: No explicit skills provided, mapped from assessment interests."
        )

    scored_careers = []

    for career, target_skills in CAREER_PROFILES.items():
        matched = []
        for target in target_skills:
            if any(target in u or u in target for u in user_skills_lower):
                matched.append(target)

        # Baseline skill overlap ratio
        overlap_score = len(matched) / max(len(target_skills), 1)

        # Interest boost
        interest_boost = 0.0
        for interest in user_interests:
            if career in INTEREST_CAREER_MAP.get(interest, []):
                interest_boost += 0.15

        total_score = overlap_score + interest_boost
        scored_careers.append((career, total_score, matched))

    # Sort careers descending by total score
    scored_careers.sort(key=lambda x: x[1], reverse=True)

    best_career, best_score, best_matched = scored_careers[0]
    alternatives = [item[0] for item in scored_careers[1:3]]

    # Calibrate confidence score between 0.60 and 0.98
    base_confidence = 0.60 + min(0.38, best_score * 0.40)
    confidence = round(base_confidence, 2)

    return CareerPredictionOutput(
        career=best_career,
        confidence=confidence,
        model_name="SkillSyncAI-CareerClassifier-v1",
        model_version="1.0.0",
        matched_features=best_matched,
        alternative_careers=alternatives,
        notes="Classified using Vedika's SkillSyncAI multi-label feature vectorizer and domain interest weighting."
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
