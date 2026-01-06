# Jobly API - Backend

FastAPI backend for the AI Job Hunter Agent - Phases 1-6 Complete

## Overview

The Jobly API is a comprehensive backend service that powers all features of the AI job hunting platform:

- **Phase 1**: User profile intake with CV parsing
- **Phase 2**: Legal job ingestion from configured sources
- **Phase 3**: AI-powered job matching with explainable rankings
- **Phase 4**: Tailored CV and application packet generation
- **Phase 5**: AI-powered interview preparation materials
- **Phase 6**: Application tracking and prefill automation support

## Tech Stack

- **FastAPI**: Modern Python web framework with async support
- **Pydantic v2**: Data validation and schema management
- **MongoDB Atlas**: Cloud-first database (recommended) with motor/pymongo
- **OpenAI API**: Embeddings for matching + GPT for interview prep
- **scikit-learn**: Cosine similarity calculations
- **Jinja2**: Template engine for LaTeX CV generation
- **PyMuPDF**: PDF text extraction
- **python-docx**: DOCX text extraction
- **httpx**: Async HTTP client for job fetching
- **feedparser**: RSS/Atom feed parsing
- **selectolax**: High-performance HTML parsing
- **PyYAML**: Job source configuration

## Prerequisites

- **Python 3.10+**
- **MongoDB Atlas account** (recommended) or local MongoDB
- **OpenAI API key** (for Phase 3 matching and Phase 5 interview prep)

## Setup

### 1. Create Virtual Environment

```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your values (see [Environment Variables](#environment-variables) section below).

**MongoDB Atlas Setup** (Recommended):
1. Create free M0 cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Configure database access (create user with password)
3. Configure network access (add your IP or `0.0.0.0/0` for dev)
4. Get connection string: Connect → Connect your application
5. Set `MONGODB_URI` in `.env`

**OpenAI API Key**:
1. Get API key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Set `OPENAI_API_KEY` in `.env`

### 4. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

### Required

```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/jobly?retryWrites=true&w=majority
OPENAI_API_KEY=sk-your_openai_api_key_here
```

### Optional (with defaults)

```bash
MONGODB_DB_NAME=jobly
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_PROVIDER=openai
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
PACKETS_DIR=/tmp/jobly_packets
```

### Match Scoring Weights (Phase 3)

Optional - customize match algorithm weights:

```bash
MATCH_WEIGHT_SEMANTIC=0.35
MATCH_WEIGHT_SKILL_OVERLAP=0.25
MATCH_WEIGHT_SENIORITY_FIT=0.15
MATCH_WEIGHT_LOCATION_FIT=0.15
MATCH_WEIGHT_RECENCY=0.10
```

See [docs/ENVIRONMENT.md](../../docs/ENVIRONMENT.md) for complete reference.

## API Endpoints

### Phase 1: Profile Management

#### POST `/profile/upload-cv`
Upload a CV file (PDF or DOCX) and get extracted profile data.

**Request**: Multipart form data with `file` field

**Response**:
```json
{
  "extracted_text": "...",
  "draft_profile": { UserProfile },
  "message": "CV processed successfully"
}
```

#### POST `/profile/save`
Save a complete user profile to MongoDB.

**Request**: UserProfile schema

**Response**:
```json
{
  "profile_id": "507f1f77bcf86cd799439011",
  "message": "Profile saved successfully"
}
```

#### GET `/profile`
Retrieve saved profile (by email or most recent).

**Query Parameters**: `email` (optional)

#### PATCH `/profile`
Update specific fields of a profile.

**Query Parameters**: `email` (required)

### Phase 2: Job Management

#### POST `/jobs/ingest`
Trigger job ingestion from configured sources.

**Response**:
```json
{
  "jobs_fetched": 42,
  "new_jobs": 15,
  "duplicates_skipped": 27,
  "sources_used": ["RemoteOK RSS", "Stack Overflow Jobs RSS"]
}
```

#### GET `/jobs`
List jobs with filters.

**Query Parameters**:
- `remote` (optional): Filter by remote type
- `country` (optional): Filter by country
- `city` (optional): Filter by city
- `keyword` (optional): Search in title/description
- `skip`, `limit`: Pagination

**Response**: List of JobPosting objects

#### GET `/jobs/{id}`
Get single job posting by ID.

#### GET `/jobs/sources/info`
Get information about configured job sources.

**Response**:
```json
{
  "sources": [
    {
      "name": "RemoteOK RSS",
      "type": "rss",
      "enabled": true,
      "compliance_note": "Public RSS feed - TOS compliant"
    }
  ]
}
```

### Phase 3: Match Management

#### POST `/matches/recompute`
Recompute all matches for current profile.

**Response**:
```json
{
  "matches_computed": 42,
  "profile_embedding_created": true
}
```

#### GET `/matches`
List matches with filters.

**Query Parameters**:
- `min_score` (optional): Minimum match score (0.0-1.0)
- `remote` (optional): Filter by remote type
- `country`, `city` (optional): Location filters
- `skill_tag` (optional): Filter by skill tag
- `skip`, `limit`: Pagination

**Response**: List of Match objects with scores and explanations

#### GET `/matches/{job_id}`
Get match details for specific job.

**Response**:
```json
{
  "job_id": "...",
  "match_score": 0.78,
  "score_breakdown": {
    "semantic_similarity": 0.82,
    "skill_overlap": 0.75,
    "seniority_fit": 0.80,
    "location_fit": 1.0,
    "recency": 0.90
  },
  "reasons": ["Strong Python skills match", "..."],
  "gaps": ["Missing React experience"],
  "recommendations": ["Consider learning React"]
}
```

### Phase 4: Packet Management

#### POST `/packets/generate`
Generate tailored CV and application packet.

**Request**:
```json
{
  "job_id": "507f1f77bcf86cd799439011",
  "include_cover_letter": true
}
```

**Response**:
```json
{
  "packet_id": "...",
  "files_generated": ["cv.tex", "cv.pdf", "cover_letter.md"],
  "tailored_summary": "...",
  "priority_skills": ["Python", "FastAPI"],
  "gaps": ["React"],
  "suggestions": ["Add React to skills section"]
}
```

#### GET `/packets`
List all generated packets.

#### GET `/packets/{packet_id}`
Get packet metadata and content.

#### GET `/packets/{packet_id}/download/{file_type}`
Download specific file from packet.

**Path Parameters**:
- `file_type`: `cv_tex`, `cv_pdf`, `cover_letter`, `recruiter_message`, `application_answers`

### Phase 5: Interview Preparation

#### POST `/interview/generate`
Generate comprehensive interview preparation materials.

**Query Parameters**: `packet_id` (required)

**Response**:
```json
{
  "packet_id": "...",
  "interview_pack": {
    "thirty_sixty_ninety": { ... },
    "star_stories": [ ... ],
    "questions_to_ask": [ ... ],
    "study_checklist": [ ... ]
  },
  "technical_qa": [
    {
      "question": "Explain Python decorators",
      "answer": "...",
      "difficulty": "medium",
      "topic": "Python",
      "grounding": { ... }
    }
  ]
}
```

#### GET `/interview/{packet_id}`
Retrieve interview pack and technical Q&A.

#### GET `/interview/{packet_id}/export`
Export interview materials as Markdown.

**Response**: Downloadable Markdown file

### Phase 6: Application Tracking & Prefill

#### POST `/applications/create`
Create application record from packet.

**Request**:
```json
{
  "packet_id": "507f1f77bcf86cd799439011"
}
```

**Response**:
```json
{
  "application_id": "...",
  "status": "prepared",
  "job_title": "Senior Python Developer",
  "company": "Acme Corp"
}
```

#### GET `/applications`
List applications with optional status filter.

**Query Parameters**: `status` (optional)

**Response**: List of Application objects

#### GET `/applications/{id}`
Get single application with full details.

#### PATCH `/applications/{id}/status`
Update application status.

**Request**:
```json
{
  "status": "applied",
  "notes": "Applied via company website"
}
```

#### POST `/prefill/create-intent`
Create prefill intent with short-lived token.

**Request**:
```json
{
  "application_id": "507f1f77bcf86cd799439011"
}
```

**Response**:
```json
{
  "intent_id": "...",
  "auth_token": "abc123...",
  "expires_at": "2024-01-15T10:30:00Z",
  "command": "npm run dev -- <intent_id> <token>"
}
```

#### GET `/prefill/intent/{intent_id}`
Fetch prefill intent (requires auth token header).

**Headers**: `X-Prefill-Token: <auth_token>`

**Response**:
```json
{
  "intent_id": "...",
  "application_id": "...",
  "job_url": "https://...",
  "profile_data": { ... },
  "resume_path": "/tmp/jobly_packets/.../cv.pdf"
}
```

#### POST `/prefill/report-result`
Report prefill automation results from local agent.

**Request**:
```json
{
  "intent_id": "...",
  "success": true,
  "fields_filled": ["name", "email", "phone"],
  "resume_uploaded": true,
  "screenshots": ["screenshot1.png", "screenshot2.png"],
  "error_message": null
}
```

## Job Source Configuration

### Configuration File

Edit `job_sources_config.yaml` to manage job sources:

```yaml
sources:
  - name: "RemoteOK RSS"
    type: "rss"
    enabled: true
    url: "https://remoteok.com/remote-dev-jobs.rss"
    compliance_note: "Public RSS feed - TOS compliant"
    rate_limit_seconds: 60

  - name: "Stack Overflow Jobs RSS"
    type: "rss"
    enabled: true
    url: "https://stackoverflow.com/jobs/feed"
    compliance_note: "Public RSS feed - TOS compliant"
    rate_limit_seconds: 60

settings:
  default_rate_limit_seconds: 60
  respect_robots_txt: true
  user_agent: "Jobly/1.0 (Job Aggregator; +https://github.com/SoroushArb/Jobly)"
```

### Adding Sources

1. **Choose legal sources**: RSS feeds, official APIs, or compliant company pages
2. **Add to config**: Include name, type, URL, and compliance note
3. **Test**: Set `enabled: false` initially, test ingestion
4. **Enable**: Set `enabled: true` after verification

See [docs/LEGAL_COMPLIANCE.md](../../docs/LEGAL_COMPLIANCE.md) for detailed guidance.

## Data Models

### UserProfile (Phase 1)
- Personal info: name, email, links
- Summary
- Skills (grouped by category)
- Experience (companies, roles, bullets with evidence refs)
- Projects
- Education
- Preferences (location, remote, skill/role tags, languages)

### JobPosting (Phase 2)
- Company, title, description
- Location (country, city, remote type)
- URL, posted date, employment type
- Source metadata (name, type, compliance note)
- Deduplication hash (SHA256)

### Match (Phase 3)
- Job reference
- Match score (0.0-1.0)
- Score breakdown (semantic, skill, seniority, location, recency)
- Explanations (reasons, gaps, recommendations)

### Packet (Phase 4)
- Job and profile references
- Generated files (CV tex/pdf, cover letter, etc.)
- Tailoring metadata (summary, priority skills, gaps, suggestions)
- Integrity notes

### InterviewPack (Phase 5)
- 30/60/90 day plan
- STAR stories with grounding references
- Questions to ask interviewer
- Study checklist

### TechnicalQA (Phase 5)
- Question, answer, follow-up questions
- Difficulty (easy/medium/hard)
- Topic
- Grounding info

### Application (Phase 6)
- Packet reference
- Job and profile references
- Status (prepared, prefilled, applied, interviewed, offered, rejected)
- Status history with timestamps
- Notes, deadline
- Created/updated timestamps

### PrefillIntent (Phase 6)
- Application reference
- Auth token (hashed), expiry
- Job URL, profile data, resume path
- Status (pending, completed, failed, expired)

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app tests/
```

### Run Specific Test File

```bash
pytest tests/test_schemas.py
```

### Syntax Validation

Before deploying or committing code, ensure all Python files have valid syntax:

```bash
# From repository root
./scripts/check_syntax.sh

# Or manually:
python -m compileall apps/api/app
```

This check is also included in the test suite (`tests/test_syntax.py`) and will catch syntax errors that would prevent Uvicorn from starting.

### Current Test Coverage

- Phase 1: Profile parsing, validation
- Phase 2: Job ingestion, deduplication
- Phase 3: Match scoring, explanations
- Phase 4: CV tailoring, packet generation
- Phase 5: Interview pack generation, Q&A
- Phase 6: Application tracking, token management
- Syntax validation: Import checks, compileall validation

All tests passing: 78/78 ✅

## Project Structure

```
apps/api/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── models/
│   │   └── database.py            # MongoDB connection
│   ├── routers/
│   │   ├── profile.py             # Phase 1: Profile endpoints
│   │   ├── jobs.py                # Phase 2: Job endpoints
│   │   ├── matches.py             # Phase 3: Match endpoints
│   │   ├── packets.py             # Phase 4: Packet endpoints
│   │   ├── interview.py           # Phase 5: Interview endpoints
│   │   ├── applications.py        # Phase 6: Application endpoints
│   │   └── prefill.py             # Phase 6: Prefill endpoints
│   ├── schemas/
│   │   ├── profile.py             # Profile Pydantic models
│   │   ├── job.py                 # Job Pydantic models
│   │   ├── match.py               # Match Pydantic models
│   │   ├── packet.py              # Packet Pydantic models
│   │   ├── interview.py           # Interview Pydantic models
│   │   └── application.py         # Application Pydantic models
│   └── services/
│       ├── cv_extractor.py        # CV parsing service
│       ├── sources/               # Job source implementations
│       │   ├── rss_source.py      # RSS feed fetcher
│       │   └── company_source.py  # HTML parser
│       ├── embedding_providers/   # Embedding abstraction
│       │   ├── base.py            # Base provider interface
│       │   └── openai_provider.py # OpenAI implementation
│       ├── llm_providers/         # LLM abstraction
│       │   ├── base.py            # Base LLM interface
│       │   └── openai_llm.py      # OpenAI GPT implementation
│       ├── match_service.py       # Match computation logic
│       ├── tailoring_service.py   # CV tailoring logic
│       ├── packet_service.py      # Packet generation
│       └── interview_service.py   # Interview generation
├── tests/                         # Unit tests
├── templates/
│   └── cv_template.tex.j2         # LaTeX CV template
├── requirements.txt               # Python dependencies
├── job_sources_config.yaml        # Job source configuration
├── example_seed_profile.json      # Example profile
└── README.md                      # This file
```

## Optional: PDF Compilation

To enable PDF generation from LaTeX CVs, install LaTeX:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install texlive-latex-base texlive-latex-extra latexmk
```

**macOS:**
```bash
brew install --cask mactex
# Or lighter version:
brew install --cask basictex
```

**Docker:**
```dockerfile
RUN apt-get update && apt-get install -y texlive-latex-base texlive-latex-extra latexmk
```

If LaTeX is not installed, `.tex` files will still be generated for manual compilation or Overleaf.

## Development

### Adding New Endpoints

1. Create/update router in `app/routers/`
2. Define Pydantic schemas in `app/schemas/`
3. Implement business logic in `app/services/`
4. Add tests in `tests/`
5. Update this README

### Database Migrations

Jobly uses MongoDB (schema-less), so no migrations are needed. Schema changes are handled via Pydantic model versioning.

### Debugging

Enable debug logging:
```bash
# Add to .env
LOG_LEVEL=DEBUG
```

Or run with debug mode:
```bash
uvicorn app.main:app --reload --log-level debug
```

## Production Deployment

### Environment Setup

- Use MongoDB Atlas (production cluster, not M0)
- Set strong credentials
- Configure IP allowlist (not `0.0.0.0/0`)
- Use separate OpenAI API key
- Set `CORS_ORIGINS` to production frontend URL
- Use persistent storage for `PACKETS_DIR`

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install LaTeX (optional)
RUN apt-get update && \
    apt-get install -y texlive-latex-base texlive-latex-extra latexmk && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t jobly-api .
docker run -p 8000:8000 \
  -e MONGODB_URI="mongodb+srv://..." \
  -e OPENAI_API_KEY="sk-..." \
  jobly-api
```

### Health Checks

Add to your deployment:
```bash
curl http://localhost:8000/docs  # Should return 200
```

## Further Documentation

- [Root README](../../README.md): Full project overview
- [Web README](../web/README.md): Frontend documentation
- [Local Agent README](../local-agent/README.md): Automation agent
- [Quickstart Guide](../../docs/QUICKSTART.md): End-to-end setup
- [Environment Variables](../../docs/ENVIRONMENT.md): Complete env var reference
- [Legal & Compliance](../../docs/LEGAL_COMPLIANCE.md): Job source guidelines
- [Troubleshooting](../../docs/TROUBLESHOOTING.md): Common issues

## License

MIT
