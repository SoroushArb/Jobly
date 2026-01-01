# Jobly

AI Job Hunter Agent - **Now with Phase 2: Job Ingestion Pipeline**

A comprehensive job hunting platform that helps you manage your professional profile, set preferences, and browse curated job postings from legal sources.

## 🚀 Features

### Phase 1: Profile Management
- **CV Upload & Parsing**: Upload PDF/DOCX files and automatically extract structured profile data
- **Profile Management**: Create, edit, and manage your professional profile
- **Job Preferences**: Set location, language, skill, and role preferences
- **Evidence Tracking**: See where each piece of information came from in your CV
- **MongoDB Storage**: Persistent storage with MongoDB Atlas

### Phase 2: Job Ingestion (NEW!)
- **Job Ingestion**: Automatically fetch jobs from legal RSS feeds and company career pages
- **Smart Deduplication**: SHA256-based deduplication prevents duplicate job postings
- **Advanced Filtering**: Filter by remote type, location, and keywords
- **Source Compliance**: Only configured sources with compliance notes are used
- **Rate Limiting**: Polite fetching with configurable rate limits
- **Job Discovery**: Browse jobs in a beautiful table interface with detail modals

## 📁 Project Structure

This is a monorepo containing:

- **`apps/api`**: FastAPI backend for CV processing, profile management, and job ingestion
- **`apps/web`**: Next.js frontend for profile management and job browsing UI

```
Jobly/
├── apps/
│   ├── api/          # FastAPI backend
│   │   ├── app/
│   │   │   ├── models/      # Database models
│   │   │   ├── routers/     # API endpoints
│   │   │   ├── schemas/     # Pydantic schemas
│   │   │   ├── services/    # Business logic
│   │   │   └── main.py      # FastAPI application
│   │   ├── tests/           # Backend tests
│   │   └── requirements.txt
│   └── web/          # Next.js frontend
│       ├── app/             # Next.js pages
│       ├── components/      # React components
│       ├── lib/             # API client
│       ├── types/           # TypeScript types
│       └── package.json
└── README.md
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic v2**: Data validation and schema management
- **MongoDB Atlas**: Cloud database (with motor/pymongo)
- **PyMuPDF**: PDF text extraction
- **python-docx**: DOCX text extraction
- **httpx**: Async HTTP client for job fetching
- **feedparser**: RSS/Atom feed parsing
- **selectolax**: High-performance HTML parsing (5-25x faster than BeautifulSoup)
- **PyYAML**: Configuration file parsing

### Frontend
- **Next.js 15**: React framework with TypeScript
- **Tailwind CSS**: Utility-first CSS framework
- **React Hooks**: State management

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB Atlas account (or local MongoDB)

## 🚀 Getting Started

### Backend Setup

1. Navigate to the API directory:
```bash
cd apps/api
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your MongoDB connection string
```

5. Run the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

### Frontend Setup

1. Navigate to the web directory:
```bash
cd apps/web
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
cp .env.local.example .env.local
# Edit .env.local if needed (defaults to localhost:8000)
```

4. Run the development server:
```bash
npm run dev
```

The web app will be available at http://localhost:3000

## 📚 Usage

### Profile Management
1. **Upload CV**: Visit http://localhost:3000/profile and upload your CV (PDF or DOCX)
2. **Review Extracted Data**: See the raw extracted text and auto-populated profile
3. **Edit Profile**: Update your name, email, skills, experience, and other details
4. **Set Preferences**: Configure your job search preferences (location, remote, skills, etc.)
5. **Save**: Save your profile to MongoDB for persistence

### Job Browsing (Phase 2)
1. **Browse Jobs**: Visit http://localhost:3000/jobs to see available job postings
2. **Trigger Ingestion**: Click "Trigger Job Ingestion" to fetch latest jobs from configured sources
3. **Filter Jobs**: Use filters for remote type, country, city, and keyword search
4. **View Details**: Click "View" on any job to see full details in a modal
5. **Apply**: Click "Apply →" to visit the original job posting

### Job Ingestion (Backend)
Configure sources in `apps/api/job_sources_config.yaml`, then:
```bash
# Via API
curl -X POST http://localhost:8000/jobs/ingest

# Via UI
# Click "Trigger Job Ingestion" button on /jobs page
```

## 🧪 Testing

### Backend Tests
```bash
cd apps/api
pytest
```

With coverage:
```bash
pytest --cov=app tests/
```

## 📖 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

**Profile Management:**
- `POST /profile/upload-cv`: Upload and parse CV
- `POST /profile/save`: Save profile to database
- `GET /profile`: Retrieve saved profile
- `PATCH /profile`: Update profile fields

**Job Management (Phase 2):**
- `POST /jobs/ingest`: Trigger job ingestion from configured sources
- `GET /jobs`: List jobs with filters (remote, country, city, keyword)
- `GET /jobs/{id}`: Get single job posting
- `GET /jobs/sources/info`: Get configured sources information

See [apps/api/README.md](apps/api/README.md) for detailed API documentation.

## 📝 Documentation

- **Phase 1**: See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for Phase 1 details
- **Phase 2**: See [PHASE2_IMPLEMENTATION.md](PHASE2_IMPLEMENTATION.md) for comprehensive Phase 2 guide
- **Example Profile**: See [apps/api/example_seed_profile.json](apps/api/example_seed_profile.json)

## 🔒 Environment Variables

### Backend (apps/api/.env)
- `MONGODB_URI`: MongoDB connection string
- `MONGODB_DB_NAME`: Database name (default: "jobly")
- `CORS_ORIGINS`: Comma-separated allowed origins (default: "http://localhost:3000")

### Frontend (apps/web/.env.local)
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: "http://localhost:8000")

## 🤝 Development Phases

**✅ Phase 1 - COMPLETE**: User Profile Intake
- CV upload and parsing (PDF/DOCX)
- Profile management with MongoDB
- Job preferences editor

**✅ Phase 2 - COMPLETE**: Job Ingestion Pipeline
- Legal job source configuration
- RSS and HTML parsing (selectolax)
- Deduplication and normalization
- Job browsing UI with filters

**🔜 Future Phases** (Not Yet Implemented):
- AI-powered job matching
- Resume tailoring for specific jobs
- Interview preparation
- Application tracking

## 📄 License

MIT

## 🎯 Acceptance Criteria

### Phase 1 ✅
✅ CV upload (PDF/DOCX) with text extraction  
✅ Schema-valid UserProfile draft generation  
✅ MongoDB Atlas integration  
✅ Editable profile screen in Next.js  
✅ Preferences editor (location, skills, roles)  
✅ Save and reload profile functionality  
✅ Evidence tracking for extracted data  
✅ Pydantic v2 validation  
✅ FastAPI endpoints with CORS  
✅ Basic unit tests (14/14 passing)

### Phase 2 ✅
✅ Running ingest stores jobs in MongoDB  
✅ Jobs appear in UI with filters working  
✅ Dedup prevents duplicates across repeated ingests  
✅ All tests passing (29/29 total)  
✅ Frontend builds successfully  
✅ Legal source compliance documented  
✅ Rate limiting implemented  
✅ Job detail modal with apply links  
✅ Editable profile screen in Next.js  
