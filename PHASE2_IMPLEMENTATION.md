# Phase 2: Job Ingestion Pipeline - Implementation Guide

## Overview

Phase 2 implements a complete job ingestion pipeline that legally collects job postings from configured sources, normalizes them into MongoDB, handles deduplication, and exposes them via API and Next.js UI.

## Architecture

### Backend Stack
- **FastAPI**: REST API endpoints for job management
- **MongoDB Atlas**: Job storage with deduplication
- **Pydantic v2**: Schema validation and data models
- **httpx**: Async HTTP client for fetching jobs
- **feedparser**: RSS/Atom feed parsing
- **selectolax**: High-performance HTML parsing (5-25x faster than BeautifulSoup)
- **PyYAML**: Configuration file parsing

### Frontend Stack
- **Next.js 16**: React framework with server-side rendering
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling

## Key Features Implemented

### 1. JobPosting Schema (Pydantic v2)

Location: `apps/api/app/schemas/job.py`

**Fields:**
- **Core Info**: company, title, url, location, country, city, remote_type
- **Description**: description_raw (HTML), description_clean (text)
- **Optional**: posted_date, employment_type
- **Source Metadata**: source_name, source_type, source_compliance_note, fetched_at
- **Deduplication**: dedupe_hash (SHA256 of normalized company+title+url)
- **Tracking**: first_seen, last_seen

**Automatic Hash Generation:**
```python
def generate_hash(self) -> str:
    normalized_company = self.company.lower().strip()
    normalized_title = self.title.lower().strip()
    normalized_url = self.url.lower().strip()
    hash_string = f"{normalized_company}|{normalized_title}|{normalized_url}"
    return hashlib.sha256(hash_string.encode()).hexdigest()
```

### 2. Source Architecture

Location: `apps/api/app/services/sources/`

**Base Interface** (`base.py`):
- `Source` abstract class defining `fetch()` and `parse()` methods
- `RawJob` dataclass for intermediate job representation
- Rate limiting and compliance tracking

**Implemented Sources:**

#### RSS Source (`rss_source.py`)
- Uses `feedparser` for RSS/Atom feeds
- Automatically extracts: title, company, description, location, dates
- HTML cleaning for descriptions
- Remote type detection from location strings

#### Company Source (`company_source.py`)
- Uses `selectolax` for HTML parsing (performance choice)
- Template-based parsing with CSS selectors
- Configurable per-company parser settings
- Automatic URL normalization (relative → absolute)

**Why selectolax over BeautifulSoup?**
- 5-25x faster parsing speed
- Lower memory footprint
- Simpler API for our CSS selector use case
- Good enough for structured career pages

### 3. Job Sources Configuration

Location: `apps/api/job_sources_config.yaml`

**Sample Configuration:**
```yaml
sources:
  - name: "Stack Overflow Jobs RSS"
    type: "rss"
    enabled: true
    url: "https://stackoverflow.com/jobs/feed"
    compliance_note: "Public RSS feed - Terms of Service compliant"
    rate_limit_seconds: 60

  - name: "Google Careers"
    type: "company"
    enabled: false  # Template not implemented yet
    url: "https://careers.google.com/jobs/results/"
    compliance_note: "Public careers page - robots.txt compliant"
    rate_limit_seconds: 120
    parser_config:
      job_list_selector: ".gc-card"
      title_selector: ".gc-card__title"
      location_selector: ".gc-card__location"
      link_selector: "a.gc-card"
```

**Compliance:**
- Only explicitly configured sources are used
- Each source has a compliance note
- Rate limiting enforced per source
- User-agent identification

### 4. Job Ingestion Service

Location: `apps/api/app/services/job_ingestion.py`

**Features:**
- Loads sources from YAML config
- Enforces rate limiting between fetches
- Handles errors gracefully (continues on failure)
- Deduplication via hash matching
- Updates last_seen for existing jobs
- Tracks first_seen for new jobs

**Deduplication Logic:**
```python
existing = await jobs_collection.find_one({"dedupe_hash": job_posting.dedupe_hash})

if existing:
    # Update last_seen only
    await jobs_collection.update_one(
        {"dedupe_hash": job_posting.dedupe_hash},
        {"$set": {"last_seen": datetime.utcnow()}}
    )
else:
    # Insert new job
    await jobs_collection.insert_one(job_dict)
```

### 5. FastAPI Endpoints

Location: `apps/api/app/routers/jobs.py`

#### `POST /jobs/ingest`
Manually trigger job ingestion from all enabled sources.

**Response:**
```json
{
  "jobs_fetched": 150,
  "jobs_new": 45,
  "jobs_updated": 105,
  "sources_processed": ["Stack Overflow Jobs RSS", "RemoteOK RSS"],
  "message": "Ingestion completed: 45 new, 105 updated"
}
```

#### `GET /jobs`
List jobs with filtering and pagination.

**Query Parameters:**
- `remote_type`: onsite/hybrid/remote/unknown
- `remote`: boolean shorthand for remote jobs
- `country`: filter by country (case-insensitive regex)
- `city`: filter by city (case-insensitive regex)
- `keyword`: search in title, company, or description
- `page`: page number (default: 1)
- `per_page`: results per page (default: 50, max: 100)

**Example:**
```bash
GET /jobs?remote_type=remote&country=Germany&keyword=python&page=1&per_page=20
```

**Response:**
```json
{
  "jobs": [...],
  "total": 234,
  "page": 1,
  "per_page": 20,
  "message": "Found 234 jobs"
}
```

#### `GET /jobs/{job_id}`
Get single job posting by MongoDB ObjectId.

#### `GET /jobs/sources/info`
Get information about configured sources.

### 6. Frontend Implementation

Location: `apps/web/app/jobs/page.tsx`

**Features:**
- Responsive job table with 6 columns:
  - Job Title (with employment type)
  - Company
  - Location (city, country)
  - Remote Type (with color-coded badges)
  - Source
  - Actions (View, Apply)

**Filters:**
- Remote Type dropdown (All/Remote/Hybrid/Onsite/Unknown)
- Country text input
- City text input
- Keyword search (searches title, company, description)
- Apply and Clear buttons

**Job Detail Modal:**
- Full job information display
- Clean description rendering
- Source compliance notes
- First/last seen dates
- Direct "Apply" link to original posting

**Pagination:**
- Previous/Next buttons
- Current page indicator
- Disabled state for edge cases

**Ingestion Trigger:**
- Button to manually trigger job ingestion
- Loading state during ingestion
- Success notification with statistics

### 7. Navigation Updates

Location: `apps/web/app/layout.tsx`

Added global navigation bar with:
- Jobly logo/home link
- Profile link
- Jobs link

Updated home page with Phase 2 features and new "Browse Jobs" card.

## Testing

### Backend Tests (29 tests, all passing)

**Job Schema Tests** (`tests/test_job_schemas.py`):
- ✅ Schema validation
- ✅ Minimal required fields
- ✅ Hash generation consistency
- ✅ Hash uniqueness for different jobs
- ✅ Case-insensitive hashing
- ✅ Optional fields (dates, employment type)
- ✅ Remote type variations

**Source Tests** (`tests/test_job_sources.py`):
- ✅ RawJob creation
- ✅ RSS source initialization and parsing
- ✅ Location parsing (city, country extraction)
- ✅ Remote type detection from location strings
- ✅ Company source initialization and parsing
- ✅ HTML cleaning

**Profile Tests** (from Phase 1):
- ✅ All 14 existing tests still passing
- No regressions introduced

### Build Verification
- ✅ Backend: All dependencies installed
- ✅ Frontend: Build successful with no TypeScript errors
- ✅ No linting issues

## Usage Guide

### Setup

1. **Install Backend Dependencies:**
```bash
cd apps/api
pip install -r requirements.txt
```

2. **Configure Environment:**
```bash
cp .env.example .env
# Edit .env with your MongoDB connection string
```

3. **Install Frontend Dependencies:**
```bash
cd apps/web
npm install
```

### Running the Application

1. **Start Backend:**
```bash
cd apps/api
uvicorn app.main:app --reload --port 8000
```

API available at: http://localhost:8000
Docs available at: http://localhost:8000/docs

2. **Start Frontend:**
```bash
cd apps/web
npm run dev
```

Web app available at: http://localhost:3000

### Using Job Ingestion

#### Via API:
```bash
# Trigger ingestion
curl -X POST http://localhost:8000/jobs/ingest

# List jobs
curl http://localhost:8000/jobs?remote_type=remote&per_page=10

# Get single job
curl http://localhost:8000/jobs/{job_id}

# Get sources info
curl http://localhost:8000/jobs/sources/info
```

#### Via UI:
1. Navigate to http://localhost:3000/jobs
2. Click "Trigger Job Ingestion" to fetch jobs
3. Use filters to refine results
4. Click "View" to see job details
5. Click "Apply →" to visit original posting

## Configuration

### Adding New RSS Sources

Edit `apps/api/job_sources_config.yaml`:

```yaml
sources:
  - name: "Your RSS Feed"
    type: "rss"
    enabled: true
    url: "https://yoursite.com/jobs.rss"
    compliance_note: "Public RSS feed - compliant with ToS"
    rate_limit_seconds: 60
```

### Adding New Company Sources

1. Add to config:
```yaml
sources:
  - name: "Company Name Careers"
    type: "company"
    enabled: true
    url: "https://company.com/careers"
    compliance_note: "Public careers page - robots.txt compliant"
    rate_limit_seconds: 120
    parser_config:
      job_list_selector: ".job-card"
      title_selector: ".job-title"
      location_selector: ".job-location"
      link_selector: "a.job-link"
```

2. Inspect the careers page to find correct CSS selectors
3. Test with a single job posting first
4. Enable the source when ready

### Database Indexes (Recommended)

For better performance, create indexes in MongoDB:

```javascript
// In MongoDB shell or Atlas
db.jobs.createIndex({ "dedupe_hash": 1 }, { unique: true })
db.jobs.createIndex({ "remote_type": 1 })
db.jobs.createIndex({ "country": 1 })
db.jobs.createIndex({ "city": 1 })
db.jobs.createIndex({ "fetched_at": -1 })
db.jobs.createIndex({ "last_seen": -1 })
```

## Security & Compliance

### Legal Compliance
- ✅ Only uses explicitly configured sources
- ✅ Each source has compliance documentation
- ✅ Rate limiting to be polite to servers
- ✅ User-agent identification
- ✅ Respects public data only (RSS feeds, public career pages)

### Data Privacy
- No personal data collected
- Only public job postings stored
- Source attribution maintained

### Security Considerations
- Input validation via Pydantic v2
- MongoDB injection prevention (parameterized queries)
- CORS configured for frontend only
- No secrets in configuration files

## Performance

### Backend
- Async HTTP requests with httpx
- Async MongoDB operations with motor
- selectolax for fast HTML parsing
- Deduplication prevents storage bloat

### Frontend
- Server-side rendering with Next.js
- Static page generation where possible
- Pagination for large result sets
- Client-side filtering without re-fetch

## Future Enhancements (Not in Scope)

The following are explicitly NOT implemented per requirements:
- ❌ Automated scheduling (cron jobs)
- ❌ AI-powered job matching
- ❌ Embeddings/vector search
- ❌ CV tailoring
- ❌ Interview generation
- ❌ Playwright automation for application prefill
- ❌ robots.txt parsing (manual compliance check required)

## Troubleshooting

### No jobs appearing after ingestion?
- Check MongoDB connection in `.env`
- Verify sources are enabled in config
- Check API logs for errors
- Ensure sources have valid URLs

### Build failures?
- Run `npm install` in apps/web
- Run `pip install -r requirements.txt` in apps/api
- Check Node.js version (18+)
- Check Python version (3.10+)

### Rate limiting issues?
- Increase `rate_limit_seconds` in source config
- Check source server status
- Verify network connectivity

## API Documentation

Full API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run backend tests:
```bash
cd apps/api
pytest -v
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## File Structure

```
apps/api/
├── app/
│   ├── routers/
│   │   └── jobs.py              # Job API endpoints
│   ├── schemas/
│   │   └── job.py               # JobPosting schemas
│   ├── services/
│   │   ├── job_ingestion.py     # Ingestion orchestration
│   │   └── sources/
│   │       ├── base.py          # Source interface
│   │       ├── rss_source.py    # RSS implementation
│   │       └── company_source.py # HTML parsing implementation
│   └── models/
│       └── database.py          # DB helpers (updated)
├── tests/
│   ├── test_job_schemas.py      # Schema tests
│   └── test_job_sources.py      # Source tests
├── job_sources_config.yaml      # Source configuration
└── requirements.txt             # Dependencies (updated)

apps/web/
├── app/
│   ├── jobs/
│   │   └── page.tsx             # Jobs listing page
│   ├── layout.tsx               # Navigation (updated)
│   └── page.tsx                 # Home page (updated)
├── types/
│   └── job.ts                   # TypeScript types
└── lib/
    └── api.ts                   # API client utilities
```

## Acceptance Criteria Status

✅ Running ingest stores jobs in MongoDB  
✅ Jobs appear in UI with filters working  
✅ Dedup prevents duplicates across repeated ingests  
✅ All tests passing (29/29)  
✅ Frontend builds successfully  
✅ API endpoints functional  
✅ TypeScript type safety  
✅ Legal compliance documented  

## Phase 2 Complete! 🎉

All requirements from the problem statement have been implemented and tested.
