# Jobly

AI Job Hunter Agent - **Now with Phase 6: Playwright-based Application Automation!**

A comprehensive job hunting platform that helps you manage your professional profile, browse curated job postings from legal sources, get AI-powered job recommendations, generate tailored application materials, prepare for interviews with AI-generated materials, and automate form filling with a local browser assistant.

## 🚀 Features

### Phase 1: Profile Management
- **CV Upload & Parsing**: Upload PDF/DOCX files and automatically extract structured profile data
- **Multi-CV Support**: Upload and manage multiple CVs, switch between them for different job applications
- **Profile Management**: Create, edit, and manage your professional profile
- **Job Preferences**: Set location, language, skill, and role preferences with working save functionality
- **Evidence Tracking**: See where each piece of information came from in your CV
- **MongoDB Storage**: Persistent storage with MongoDB Atlas
- **CV Library**: View all uploaded CVs, set active CV for matching

### Phase 2: Job Ingestion
- **Job Ingestion**: Automatically fetch jobs from legal RSS feeds and company career pages
- **Multiple Sources**: Supports Stack Overflow, RemoteOK, We Work Remotely, Remote.co, Hacker News, and more
- **Manual Job Import**: Import jobs from LinkedIn/Indeed by providing URL and basic info (no scraping required)
- **Smart Deduplication**: SHA256-based deduplication prevents duplicate job postings
- **Advanced Filtering**: Filter by remote type, location, job title, and keywords
- **Title-Specific Search**: Dedicated job title search for more relevant results
- **Source Compliance**: Only configured sources with compliance notes are used
- **Rate Limiting**: Polite fetching with configurable rate limits
- **Job Discovery**: Browse jobs in a beautiful table interface with detail modals

### Phase 3: AI-Powered Job Matching
- **Hybrid Scoring**: Multi-dimensional match scoring combining:
  - Semantic similarity (embeddings-based)
  - Skill overlap analysis
  - Seniority fit matching
  - Location preference alignment
  - Job recency weighting
- **Explainable AI**: Every match includes:
  - Top reasons why it's a good match
  - Identified gaps and missing skills
  - Actionable recommendations to improve candidacy
- **Smart Embeddings**: OpenAI-powered semantic understanding with MongoDB caching
- **Swappable Providers**: Embedding provider abstraction allows easy switching between AI services
- **Ranked Matches**: Jobs sorted by match score with detailed breakdowns

### Phase 4: Tailored CV Generation & Application Packets
- **Tailored CVs**: Generate job-specific CVs with:
  - Rewritten summary mentioning target company and role
  - Prioritized skills matching job requirements
  - LaTeX format for professional typesetting
  - PDF compilation when latexmk is available
  - Deterministic 2-page layout control
- **Application Packet**: Complete application materials for each job:
  - CV (.tex and .pdf)
  - Cover letter (optional)
  - Recruiter outreach message
  - Common application question answers
- **Truthful Output**: No fabricated claims or invented experience
  - Integrity notes warn about missing requirements
  - Gap analysis shows what's lacking
  - Evidence-based bullet suggestions
- **One-Click Generation**: Generate complete packet from matches page
- **Download & Apply**: All materials ready to download and use

### Phase 5: AI-Powered Interview Preparation (NEW!)
- **Interview Pack**: Comprehensive preparation materials including:
  - 30/60/90 day plan tailored to the role
  - STAR format stories grounded in your real experience
  - Thoughtful questions to ask the interviewer
  - Study checklist for identified skill gaps
- **Technical Q&A**: Gap-aware technical interview preparation:
  - Questions prioritized based on your weak areas
  - 3 difficulty levels (easy/medium/hard) per topic
  - High-quality answers with follow-up questions
  - Searchable and filterable by topic/difficulty
- **Grounding & Truth**: All content based on real data
  - STAR stories reference actual experience bullets
  - Company info limited to job description only
  - Integrity notes for missing information
  - No fabricated claims or invented facts
- **LLM-Powered Generation**: OpenAI GPT-4o-mini with structured output
  - Swappable provider architecture
  - Retry logic and validation
  - Safe fallback on failures
- **Export to Markdown**: Download complete prep pack for offline study

### Phase 6: Application Automation & Tracking (NEW!)
- **Local Browser Automation**: Playwright-based prefill assistant
  - Runs on your macOS machine (not in cloud)
  - Opens real browser to job application pages
  - Automatically detects ATS type (Greenhouse, Lever, etc.)
  - Prefills form fields with your profile data
  - Attaches your tailored CV PDF
  - Takes screenshots at each step
  - Stops before submit for safety and review
- **Security-First Design**: Short-lived tokens and local execution
  - 15-minute token expiry
  - Tokens shown only once
  - No passwords stored
  - All automation happens locally
- **Application Tracking**: Full pipeline management
  - Track applications from prepared to offered
  - Status history with audit trail
  - Notes and deadline tracking
  - Visual dashboard with filtering
- **ATS Support**: 
  - ✅ Greenhouse (fully implemented)
  - ✅ Lever (fully implemented)
  - ✅ Generic fallback for unknown systems
  - 🚧 Workday (detection only)
  - 🚧 LinkedIn Easy Apply (detection only)

### Phase 7: Production & Deployment (NEW!)
- **Background Jobs**: Long-running operations as async jobs
  - Job ingestion via background worker
  - Match recomputation in background
  - Packet generation async
  - Interview generation async
  - Job queue with atomic locking
- **Real-time Updates**: Server-Sent Events (SSE)
  - Live progress updates for all background jobs
  - Application status change notifications
  - Event history for reconnection support
- **GridFS Storage**: Production-safe file storage
  - MongoDB GridFS for artifacts (CVs, packets)
  - Filesystem fallback for local development
  - Metadata tracking and cleanup
- **Production Hardening**:
  - Health (`/healthz`) and readiness (`/readyz`) endpoints
  - Request ID tracking and structured logging
  - Centralized error handling with stable JSON
  - Environment validation at startup
  - Database indexes for performance
- **Docker & Koyeb**: Full containerization support
  - Dockerfiles for API, Worker, and Web
  - docker-compose for local development
  - Complete Koyeb deployment guide
  - Environment variable documentation

## 📁 Project Structure

This is a monorepo containing:

- **`apps/api`**: FastAPI backend for CV processing, profile management, job ingestion, and application tracking
- **`apps/worker`**: Background worker for async job processing (uses API codebase)
- **`apps/web`**: Next.js frontend for profile management, job browsing, and application tracking UI
- **`apps/local-agent`**: Node.js + Playwright local automation agent for form prefilling

```
Jobly/
├── apps/
│   ├── api/          # FastAPI backend
│   │   ├── app/
│   │   │   ├── models/      # Database models
│   │   │   ├── routers/     # API endpoints
│   │   │   ├── schemas/     # Pydantic schemas
│   │   │   ├── services/    # Business logic
│   │   │   ├── middleware/  # Error handling, request tracking
│   │   │   └── main.py      # FastAPI application
│   │   ├── tests/           # Backend tests
│   │   ├── requirements.txt
│   │   └── Dockerfile       # Container image for API
│   ├── worker/       # Background job processor
│   │   ├── handlers/        # Job type handlers
│   │   ├── worker.py        # Worker entry point
│   │   └── Dockerfile       # Container image for worker
│   ├── web/          # Next.js frontend
│   │   ├── app/             # Next.js pages
│   │   ├── components/      # React components
│   │   ├── lib/             # API client
│   │   ├── types/           # TypeScript types
│   │   ├── package.json
│   │   └── Dockerfile       # Container image for web
│   └── local-agent/  # Playwright automation agent
│       ├── src/
│       │   ├── adapters/    # ATS adapters
│       │   ├── utils/       # API client & services
│       │   └── index.ts     # Entry point
│       ├── package.json
│       └── README.md
├── docs/             # Documentation
│   └── DEPLOY_KOYEB.md  # Deployment guide
├── docker-compose.yml   # Local development with Docker
└── README.md
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic v2**: Data validation and schema management
- **MongoDB Atlas**: Cloud database (with motor/pymongo)
- **OpenAI API**: Embeddings for semantic matching + LLM for interview prep
- **scikit-learn**: Cosine similarity calculations
- **Jinja2**: Template engine for LaTeX CV generation
- **PyMuPDF**: PDF text extraction
- **python-docx**: DOCX text extraction

### Local Agent
- **Node.js 18+**: JavaScript runtime
- **TypeScript**: Type-safe development
- **Playwright**: Browser automation framework
- **Axios**: HTTP client for API communication
- **httpx**: Async HTTP client for job fetching
- **feedparser**: RSS/Atom feed parsing
- **selectolax**: High-performance HTML parsing (5-25x faster than BeautifulSoup)
- **PyYAML**: Configuration file parsing

### Frontend
- **Next.js 16**: React framework with TypeScript
- **Tailwind CSS**: Utility-first CSS framework
- **React Hooks**: State management

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- **MongoDB Atlas account** (recommended - free tier works great)
- OpenAI API key (for Phase 3 matching and Phase 5 interview prep)

## 📖 Documentation

- **[Quickstart Guide](docs/QUICKSTART.md)** - Get up and running in minutes with MongoDB Atlas
- **[Environment Variables](docs/ENVIRONMENT.md)** - Complete environment variable reference
- **[Legal & Compliance](docs/LEGAL_COMPLIANCE.md)** - Job source legal guidelines and best practices
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Per-App Documentation

- **[API Documentation](apps/api/README.md)** - Backend setup, endpoints, and development
- **[Web Documentation](apps/web/README.md)** - Frontend setup, routes, and workflows
- **[Local Agent Documentation](apps/local-agent/README.md)** - Browser automation setup and usage

### Phase Implementation Details

- **Phase 1**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Phase 2**: [PHASE2_IMPLEMENTATION.md](PHASE2_IMPLEMENTATION.md)
- **Phase 3**: [PHASE3_IMPLEMENTATION.md](PHASE3_IMPLEMENTATION.md)
- **Phase 4**: [PHASE4_IMPLEMENTATION.md](PHASE4_IMPLEMENTATION.md)
- **Phase 5**: [PHASE5_IMPLEMENTATION.md](PHASE5_IMPLEMENTATION.md)
- **Phase 6**: [PHASE6_IMPLEMENTATION.md](PHASE6_IMPLEMENTATION.md)

## 🚀 Getting Started

**New to Jobly?** Follow the [Quickstart Guide](docs/QUICKSTART.md) for a step-by-step setup with MongoDB Atlas.

### Backend Setup

**Recommended**: Use [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (free tier available). See [Quickstart Guide](docs/QUICKSTART.md) for detailed Atlas setup.

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
# Edit .env with your MongoDB Atlas connection string and OpenAI API key
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/jobly?...
# OPENAI_API_KEY=sk-your_key_here
```

See [ENVIRONMENT.md](docs/ENVIRONMENT.md) for complete environment variable reference.

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

## 🚢 Production Deployment

Jobly is production-ready and can be deployed to cloud platforms like Koyeb, Heroku, or any container platform.

### Quick Deploy to Koyeb

Jobly includes full Docker support and a comprehensive deployment guide for Koyeb:

1. **Architecture**: 3 services (API, Worker, Web) + MongoDB Atlas
2. **Storage**: GridFS for production artifact storage
3. **Real-time**: Server-Sent Events (SSE) for live progress updates
4. **Background Jobs**: Async processing for long-running operations
5. **Health Checks**: `/healthz` and `/readyz` endpoints
6. **Monitoring**: Request IDs, structured logging, error handling

**See the complete guide**: [docs/DEPLOY_KOYEB.md](docs/DEPLOY_KOYEB.md)

#### Koyeb Configuration Quick Reference

**Deploy two services** (API and Web) to Koyeb using GitHub integration:

**Important**: Koyeb uses the repository root as the Docker build context, even when specifying a Dockerfile path. The Dockerfiles are already configured to handle this correctly—you only need to set the Dockerfile path, not a custom build context.

**API Service:**
- Dockerfile location: `apps/api/Dockerfile`
- Build context: Repository root (automatic, no configuration needed)
- Required environment variables:
  - `MONGODB_URI` - MongoDB Atlas connection string
  - `MONGODB_DB_NAME` - Database name (recommended: "jobly")
  - `CORS_ORIGINS` - Your web app URL for CORS
- Optional environment variables:
  - `OPENAI_API_KEY` - For AI matching and interview prep features
- Health check: HTTP GET on `/docs` or `/healthz`

**Web Service:**
- Dockerfile location: `apps/web/Dockerfile`
- Build context: Repository root (automatic, no configuration needed)
- Required environment variables:
  - `NEXT_PUBLIC_API_URL` - Your API service URL (e.g., https://your-api.koyeb.app)
  - Must be set at build time for Next.js
- Health check: HTTP GET on `/`

Both services will bind to Koyeb's `$PORT` environment variable with sensible fallbacks (8000 for API, 3000 for Web).

### Key Features for Production

#### Background Jobs & Real-time Updates
- Job ingestion, match computation, packet generation, and interview prep run as background jobs
- Real-time progress updates via SSE (Server-Sent Events)
- Dedicated worker service processes jobs asynchronously
- Job queue with atomic locking and automatic retry on failures

#### GridFS Storage
- Production-safe file storage using MongoDB GridFS
- Supports large files (CVs, packets, attachments)
- Automatic cleanup and metadata tracking
- Falls back to filesystem for local development

#### Production Hardening
- ✅ Centralized error handling with stable JSON format
- ✅ Request ID tracking for debugging
- ✅ Structured logging with request context
- ✅ Health and readiness endpoints
- ✅ Environment validation at startup
- ✅ Database indexes for optimal performance
- ✅ CORS configuration via environment

### Docker Support

Run locally with Docker Compose:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=sk-your-key-here

# Start all services
docker-compose up
```

This starts:
- MongoDB (local)
- API service on http://localhost:8000
- Worker service (background jobs)
- Web service on http://localhost:3000

Individual Dockerfiles for each service:
- `apps/api/Dockerfile` - API service
- `apps/worker/Dockerfile` - Background worker
- `apps/web/Dockerfile` - Next.js frontend

## 📚 Usage

### Profile Management
1. **Upload CV**: Visit http://localhost:3000/profile and upload your CV (PDF or DOCX)
2. **Review Extracted Data**: See the raw extracted text and auto-populated profile
3. **Edit Profile**: Update your name, email, skills, experience, and other details
4. **Set Preferences**: Configure your job search preferences (location, remote, skills, etc.)
5. **Save**: Click "Save Profile" or "Save Preferences" to persist your data
6. **Multi-CV**: Upload multiple CVs and switch between them using the CV Library section
7. **Set Active CV**: Choose which CV to use for job matching and applications

### Job Browsing (Phase 2)
1. **Browse Jobs**: Visit http://localhost:3000/jobs to see available job postings
2. **Trigger Ingestion**: Click "Trigger Job Ingestion" to fetch latest jobs from configured sources
3. **Filter Jobs**: Use filters for:
   - **Job Title**: Search specifically in job titles for better relevance
   - **Remote Type**: Filter by remote, hybrid, onsite, or unknown
   - **Country/City**: Filter by location
   - **Keyword**: Search across title, company, and description
4. **View Details**: Click "View" on any job to see full details in a modal
5. **Apply**: Click "Apply →" to visit the original job posting
6. **Manual Import**: Import jobs from LinkedIn/Indeed using the manual import feature (no scraping)

### Job Matching (Phase 3)
1. **Ensure Prerequisites**: Make sure you have:
   - A saved profile with skills and preferences
   - Jobs ingested in the database
   - OpenAI API key configured in `.env`
2. **Compute Matches**: Visit http://localhost:3000/matches and click "Recompute Matches"
3. **Browse Matches**: View ranked job matches sorted by score
4. **Filter Matches**: Apply filters for minimum score, remote type, location, etc.
5. **View Details**: Click "View Details" to see:
   - Match score breakdown
   - Top reasons for the match
   - Potential gaps
   - Actionable recommendations
6. **Apply**: Click "Apply for This Job" to visit the original posting

### Tailored CV Generation (Phase 4)
1. **Generate Packet**: From the Matches page, click "Generate Packet" for any job
2. **View Packet**: You'll be redirected to the packet detail page showing:
   - Tailored professional summary
   - Priority skills for this job
   - Identified gaps
   - Suggested bullet improvements
   - Integrity notes
3. **Download Files**: Download any of the generated materials:
   - CV (LaTeX .tex file - always available)
   - CV (PDF - if LaTeX compilation is available)
   - Cover Letter (if requested)
   - Recruiter Message
   - Common Application Answers
4. **Use Materials**: Use the downloaded files in your application

### Interview Preparation (Phase 5)
1. **Generate Interview Materials**: From the Packet page, click "Prepare Interview"
2. **AI Generation**: System creates comprehensive interview prep including:
   - 30/60/90 day plan for the role
   - STAR stories grounded in your real experience
   - Questions to ask the interviewer
   - Study checklist for skill gaps
   - Technical Q&A prioritized by your weak areas
3. **Review Materials**: Browse the interview prep page with:
   - Organized sections for each component
   - Color-coded 30/60/90 plan
   - Expandable STAR stories with grounding references
   - Categorized interview questions
   - Interactive study checklist
4. **Search & Filter**: In the Technical Q&A section:
   - Search questions, answers, or concepts
   - Filter by difficulty (easy/medium/hard)
   - Browse by topic
5. **Export**: Download complete prep pack as Markdown for offline study
6. **Prepare**: Practice STAR stories, review technical answers, study gaps

### Application Automation (Phase 6)
1. **Setup Local Agent** (one-time):
   ```bash
   cd apps/local-agent
   npm install
   npx playwright install chromium
   ```

2. **Create Application**: From Packet page, click "Open & Prefill"
   - System creates application record
   - Generates prefill intent with short-lived token
   - UI displays command to run

3. **Run Local Agent**: Copy command from UI and run in terminal
   ```bash
   npm run dev -- <intent_id> <auth_token>
   ```

4. **Watch Automation**:
   - Browser launches automatically
   - Navigates to job application page
   - Detects ATS type (Greenhouse, Lever, etc.)
   - Fills form fields with your data
   - Uploads tailored resume
   - Takes screenshots
   - Stops before submit (safety!)

5. **Review & Submit**:
   - Review filled form in browser
   - Correct any errors
   - Answer any custom questions
   - Click submit manually when satisfied

6. **Track Application**: Go to Applications page
   - View all applications with status
   - Filter by status (prepared, prefilled, applied, etc.)
   - Update status as you progress through pipeline

#### PDF Compilation (Optional)
To enable PDF generation, install LaTeX on your server:

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
Add to your Dockerfile:
```dockerfile
RUN apt-get update && apt-get install -y texlive-latex-base texlive-latex-extra latexmk
```

If LaTeX is not installed, the system will still generate .tex files that you can compile locally or on Overleaf.

### Job Ingestion (Backend)
Configure sources in `apps/api/job_sources_config.yaml`, then:
```bash
# Via API
curl -X POST http://localhost:8000/jobs/ingest

# Via UI
# Click "Trigger Job Ingestion" button on /jobs page
```

### Match Computation (Backend)
```bash
# Recompute all matches
curl -X POST http://localhost:8000/matches/recompute

# Get matches with filters
curl "http://localhost:8000/matches?min_score=0.5&remote=true"

# Get match for specific job
curl http://localhost:8000/matches/{job_id}
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
- `POST /profile/upload-cv`: Upload and parse CV (now stores CV document and returns CV ID)
- `POST /profile/save`: Save profile to database
- `GET /profile`: Retrieve saved profile
- `PATCH /profile`: Update profile fields
- `POST /profile/preferences/save`: Save job search preferences with confirmation

**CV Management (Multi-CV):**
- `GET /cvs`: List all CVs for a user
- `POST /cvs/set-active`: Set a CV as active for matching
- `DELETE /cvs/{cv_id}`: Delete a CV
- `GET /cvs/active`: Get currently active CV

**Job Management (Phase 2):**
- `POST /jobs/ingest`: Trigger job ingestion from configured sources
- `GET /jobs`: List jobs with filters (remote, country, city, keyword, title)
- `GET /jobs/{id}`: Get single job posting
- `GET /jobs/sources/info`: Get configured sources information
- `POST /jobs/manual-import`: Manually import a job from URL (for LinkedIn/Indeed)

**Match Management (Phase 3):**
- `POST /matches/recompute`: Recompute all matches for current profile
- `GET /matches`: List matches with filters (min_score, remote, location, skill_tag)
- `GET /matches/{job_id}`: Get match details for specific job

**Packet Management (Phase 4):**
- `POST /packets/generate`: Generate tailored CV and application packet
- `GET /packets/{packet_id}`: Get packet metadata
- `GET /packets`: List all packets
- `GET /packets/{packet_id}/download/{file_type}`: Download specific file

**Interview Prep (Phase 5):**
- `POST /interview/generate?packet_id=...`: Generate interview preparation materials
- `GET /interview/{packet_id}`: Get interview pack and technical Q&A

**Application Tracking (Phase 6):**
- `POST /applications/create`: Create application from packet
- `GET /applications`: List applications with status filter
- `GET /applications/{id}`: Get single application
- `PATCH /applications/{id}/status`: Update application status

**Prefill Automation (Phase 6):**
- `POST /prefill/create-intent`: Create prefill intent with token
- `GET /prefill/intent/{id}`: Fetch intent (requires auth token)
- `POST /prefill/report-result`: Report prefill results from local agent

See [apps/api/README.md](apps/api/README.md) for detailed API documentation.

## 🔒 Environment Variables

**MongoDB Atlas** (recommended):
- Free M0 tier available
- Automatic backups and scaling
- Simple connection string setup

See [ENVIRONMENT.md](docs/ENVIRONMENT.md) for complete environment variable reference and setup guide.

### Quick Reference

**Backend** (`apps/api/.env`):
- `MONGODB_URI` - MongoDB Atlas connection string (required)
- `OPENAI_API_KEY` - OpenAI API key (required for Phase 3+)
- `MONGODB_DB_NAME` - Database name (default: "jobly")
- `CORS_ORIGINS` - Allowed CORS origins
- Plus optional: embedding/LLM models, match weights, packet directory

**Frontend** (`apps/web/.env.local`):
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: "http://localhost:8000")

**Local Agent** (`apps/local-agent/.env`):
- `API_URL` - Backend API URL
- `STOP_BEFORE_SUBMIT` - Safety flag (recommended: true)
- Plus optional: headless mode, screenshot directory

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

**✅ Phase 3 - COMPLETE**: AI-Powered Job Matching
- Hybrid scoring (semantic + skill + seniority + location + recency)
- Explainable AI with reasons, gaps, and recommendations
- OpenAI embeddings with MongoDB caching
- Swappable embedding providers
- Match ranking and filtering UI

**✅ Phase 4 - COMPLETE**: Tailored CV Generation & Application Packets
- LaTeX CV generation with job-specific tailoring
- Complete application packets (CV, cover letter, recruiter message, answers)
- PDF compilation support
- Truthful output with integrity notes
- Gap analysis and skill prioritization

**✅ Phase 5 - COMPLETE**: AI-Powered Interview Preparation
- LLM-powered interview pack generation
- STAR stories grounded in real experience
- 30/60/90 day plans
- Gap-aware technical Q&A
- Searchable question library
- Markdown export for offline study

**✅ Phase 6 - COMPLETE**: Application Automation & Tracking
- Local Playwright-based prefill assistant
- Secure token-based authentication
- ATS detection (Greenhouse, Lever, generic)
- Automatic form filling and resume upload
- Screenshot capture at each step
- Application status tracking pipeline
- Safety stops before submission

**🔜 Future Phases** (Not Yet Implemented):
- Phase 7: Advanced analytics and insights
- Phase 8: Team collaboration features

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

### Phase 3 ✅
✅ Hybrid scoring with 5 components (semantic, skill, seniority, location, recency)  
✅ OpenAI embedding provider with swappable interface  
✅ Embedding caching in MongoDB  
✅ Match generation and storage in MongoDB  
✅ Explainable AI (reasons, gaps, recommendations)  
✅ Deterministic scoring with stable tie-breakers  
✅ API endpoints for match computation and retrieval  
✅ Matches UI with ranked table and detail modals  
✅ All tests passing (50/50 total)  
✅ Frontend builds successfully  

### Phase 4 ✅
✅ Tailoring service with skill extraction and gap analysis  
✅ LaTeX CV generation with Jinja2 templates  
✅ PDF compilation support (optional)  
✅ Complete application packets (CV, cover letter, recruiter message, answers)  
✅ Packet storage with file integrity (SHA256)  
✅ Truthful output with integrity notes  
✅ API endpoints for packet generation and retrieval  
✅ Packet detail UI with download links  
✅ All tests passing (63/63 total)  
✅ Frontend builds successfully  

### Phase 5 ✅
✅ LLM provider abstraction with OpenAI implementation  
✅ Structured output generation with JSON schema validation  
✅ Interview pack with 30/60/90 plan, STAR stories, questions, study checklist  
✅ Technical Q&A with gap-aware prioritization  
✅ Grounding references linking STAR stories to real experience  
✅ Content restrictions (job description only, no fabrication)  
✅ API endpoints for interview generation and retrieval  
✅ Interview viewer UI with search and filter  
✅ Markdown export functionality  
✅ All tests passing (78/78 total)  
✅ Frontend builds successfully  
