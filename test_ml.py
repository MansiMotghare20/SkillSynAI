"""
Automated unit tests for Vedika's SkillSyncAI Python ML Microservice.
Tests health check, prediction with skills, prediction without skills, and interest weighting.
"""
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_ml_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "supported_careers" in data
    assert "Data Scientist" in data["supported_careers"]

def test_predict_career_with_data_science_skills():
    payload = {
        "skills": ["python", "pandas", "numpy", "sql", "statistics"],
        "education": "B.Tech Computer Science",
        "experience": "Intermediate",
        "interests": ["Data Science", "AI / ML"]
    }
    response = client.post("/predict-career", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["career"] in ["Data Scientist", "Machine Learning Engineer"]
    assert data["confidence"] >= 0.60
    assert len(data["matched_features"]) > 0

def test_predict_career_with_web_skills():
    payload = {
        "skills": ["react", "javascript", "tailwind css", "html5"],
        "education": "BCA",
        "experience": "Beginner",
        "interests": ["Web Development"]
    }
    response = client.post("/predict-career", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["career"] in ["Frontend Engineer", "Full Stack Developer"]
    assert "react" in [f.lower() for f in data["matched_features"]]

def test_predict_career_empty_skills_fallback():
    payload = {
        "skills": [],
        "interests": ["Cybersecurity"]
    }
    response = client.post("/predict-career", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["career"] == "Cybersecurity Analyst"
    assert data["confidence"] > 0.50
