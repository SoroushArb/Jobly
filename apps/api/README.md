# Jobly API - Backend

FastAPI backend for the AI Job Hunter Agent - Phase 1: User Profile Intake

## Features

- **CV Upload & Parsing**: Upload PDF/DOCX files and extract structured profile data
- **Profile Management**: Create, read, update user profiles
- **MongoDB Integration**: Persistent storage with MongoDB Atlas
- **Pydantic v2 Validation**: Strict schema validation for all data
- **Evidence Tracking**: Track where each piece of information came from in the CV

## Setup

### Prerequisites

- Python 3.10+
- MongoDB Atlas account (or local MongoDB)

### Installation

1. Create and activate virtual environment:
```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your MongoDB connection string
```

### Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Profile Management

#### POST /profile/upload-cv
Upload a CV file (PDF or DOCX) and get extracted profile data.

**Request:**
- Multipart form data with `file` field

**Response:**
```json
{
  "extracted_text": "...",
  "draft_profile": { UserProfile object },
  "message": "CV processed successfully"
}
```

#### POST /profile/save
Save a complete user profile to MongoDB.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  ...
}
```

**Response:**
```json
{
  "profile_id": "507f1f77bcf86cd799439011",
  "message": "Profile saved successfully"
}
```

#### GET /profile
Retrieve a saved profile.

**Query Parameters:**
- `email` (optional): Email address of profile to retrieve. If not provided, returns most recent profile.

**Response:**
```json
{
  "profile": { UserProfile object },
  "message": "Profile retrieved successfully"
}
```

#### PATCH /profile
Update specific fields of a profile.

**Query Parameters:**
- `email` (required): Email address of profile to update

**Request:**
```json
{
  "name": "Updated Name",
  "summary": "Updated summary"
}
```

**Response:**
```json
{
  "profile_id": "507f1f77bcf86cd799439011",
  "message": "Profile updated successfully"
}
```

## Schema

### UserProfile

Complete user profile with the following structure:

- `name`: string
- `email`: string (email format)
- `links`: list of URLs
- `summary`: optional string
- `skills`: list of SkillGroup objects
  - `category`: string (e.g., "Programming Languages")
  - `skills`: list of strings
- `experience`: list of ExperienceRole objects
  - `company`: string
  - `title`: string
  - `dates`: string
  - `bullets`: list of ExperienceBullet objects
    - `text`: string
    - `evidence_ref`: optional string (e.g., "page 1")
  - `tech`: list of strings
- `projects`: list of Project objects
- `education`: list of Education objects
- `preferences`: Preferences object
  - `europe`: boolean
  - `remote`: boolean
  - `countries`: list of strings
  - `cities`: list of strings
  - `skill_tags`: list of strings
  - `role_tags`: list of strings
  - `visa_required`: optional boolean
  - `languages`: list of strings
- `schema_version`: string (default: "1.0.0")
- `updated_at`: datetime

See `example_seed_profile.json` for a complete example.

## Testing

Run tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app tests/
```

## Project Structure

```
apps/api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py      # MongoDB connection
│   ├── routers/
│   │   ├── __init__.py
│   │   └── profile.py       # Profile endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── profile.py       # Pydantic models
│   └── services/
│       ├── __init__.py
│       └── cv_extractor.py  # CV parsing logic
├── tests/
│   ├── __init__.py
│   ├── test_schemas.py
│   └── test_cv_extractor.py
├── requirements.txt
├── .env.example
└── README.md
```

## Environment Variables

- `MONGODB_URI`: MongoDB connection string
- `MONGODB_DB_NAME`: Database name (default: "jobly")
- `CORS_ORIGINS`: Comma-separated list of allowed origins (default: "http://localhost:3000")

## Notes

- CV extraction is heuristic-based and may not be perfect for all formats
- No data is hallucinated - unknown fields are left empty
- Evidence references track where information came from in the original CV
