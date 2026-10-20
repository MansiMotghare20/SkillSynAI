# SkillSyncAI — ML Microservice Integration Guide (For Vedika)

This microservice provides career path classification and prediction endpoints for the SkillSyncAI platform. It is designed to host your trained Scikit-Learn / PyTorch model or rule-based multi-label feature vectorizer.

## Endpoint Contract

### 1. Health Check
- **URL:** `GET /health`
- **Response:**
```json
{
  "status": "healthy",
  "service": "SkillSyncAI ML Inference Microservice",
  "model_version": "1.0.0",
  "author": "Vedika (SkillSyncAI Team)",
  "supported_careers": ["Full Stack Developer", "Data Scientist", "..."]
}
```

### 2. Career Prediction
- **URL:** `POST /predict-career`
- **Request Body:**
```json
{
  "skills": ["Python", "Pandas", "SQL", "Statistics"],
  "education": "B.Tech Computer Science",
  "experience": "Intermediate",
  "interests": ["Data Science", "AI / ML"],
  "preferredDomain": "Data Science"
}
```

- **Response Body:**
```json
{
  "career": "Data Scientist",
  "confidence": 0.88,
  "model_name": "SkillSyncAI-CareerClassifier-v1",
  "model_version": "1.0.0",
  "matched_features": ["python", "pandas", "sql", "statistics"],
  "alternative_careers": ["Machine Learning Engineer", "Data Analyst"],
  "notes": "Classified using Vedika's SkillSyncAI multi-label feature vectorizer and domain interest weighting."
}
```

## How to Run Locally

1. Create a Python virtual environment (recommended):
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the FastAPI server on port 8000:
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

4. Run automated tests:
```bash
pytest test_ml.py
```
