# Jobly

AI Job Hunter Agent - **Now with Phase 6: Playwright-based Application Automation!**

A comprehensive job hunting platform that helps you manage your professional profile, browse curated job postings from legal sources, get AI-powered job recommendations, generate tailored application materials, prepare for interviews with AI-generated materials, and automate form filling with a local browser assistant.

## 🚀 Features

### Phase 1: Profile Management
- **CV Upload & Parsing**: Upload PDF/DOCX files and automatically extract structured profile data
- **Profile Management**: Create, edit, and manage your professional profile
- **Job Preferences**: Set location, language, skill, and role preferences
- **Evidence Tracking**: See where each piece of information came from in your CV
- **MongoDB Storage**: Persistent storage with MongoDB Atlas

### Phase 2: Job Ingestion
- **Job Ingestion**: Automatically fetch jobs from legal RSS feeds and company career pages
- **Smart Deduplication**: SHA256-based deduplication prevents duplicate job postings
- **Advanced Filtering**: Filter by remote type, location, and keywords
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

## 📁 Project Structure

This is a monorepo containing:

- **`apps/api`**: FastAPI backend for CV processing, profile management, job ingestion, and application tracking
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
│   │   │   └── main.py      # FastAPI application
│   │   ├── tests/           # Backend tests
│   │   └── requirements.txt
│   ├── web/          # Next.js frontend
│   │   ├── app/             # Next.js pages
│   │   ├── components/      # React components
│   │   ├── lib/             # API client
│   │   ├── types/           # TypeScript types
│   │   └── package.json
│   └── local-agent/  # Playwright automation agent
│       ├── src/
│       │   ├── adapters/    # ATS adapters
│       │   ├── utils/       # API client & services
│       │   └── index.ts     # Entry point
│       ├── package.json
│       └── README.md
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
- MongoDB Atlas account (or local MongoDB)
- OpenAI API key (for Phase 3 matching and Phase 5 interview prep)

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
# Edit .env with your MongoDB connection string and OpenAI API key
# Required for Phase 3: OPENAI_API_KEY=your_key_here (embeddings)
# Required for Phase 5: Same OPENAI_API_KEY (interview generation)
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
- `POST /profile/upload-cv`: Upload and parse CV
- `POST /profile/save`: Save profile to database
- `GET /profile`: Retrieve saved profile
- `PATCH /profile`: Update profile fields

**Job Management (Phase 2):**
- `POST /jobs/ingest`: Trigger job ingestion from configured sources
- `GET /jobs`: List jobs with filters (remote, country, city, keyword)
- `GET /jobs/{id}`: Get single job posting
- `GET /jobs/sources/info`: Get configured sources information

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

## 📝 Documentation

- **Phase 1**: See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for Phase 1 details
- **Phase 2**: See [PHASE2_IMPLEMENTATION.md](PHASE2_IMPLEMENTATION.md) for comprehensive Phase 2 guide
- **Phase 3**: See [PHASE3_IMPLEMENTATION.md](PHASE3_IMPLEMENTATION.md) for Phase 3 matching details
- **Phase 4**: See [PHASE4_IMPLEMENTATION.md](PHASE4_IMPLEMENTATION.md) for Phase 4 tailoring details
- **Phase 5**: See [PHASE5_IMPLEMENTATION.md](PHASE5_IMPLEMENTATION.md) for Phase 5 interview prep details
- **Phase 6**: See [PHASE6_IMPLEMENTATION.md](PHASE6_IMPLEMENTATION.md) for Phase 6 automation details
- **Local Agent**: See [apps/local-agent/README.md](apps/local-agent/README.md) for setup instructions
- **Example Profile**: See [apps/api/example_seed_profile.json](apps/api/example_seed_profile.json)

## 🔒 Environment Variables

### Backend (apps/api/.env)
- `MONGODB_URI`: MongoDB connection string
- `MONGODB_DB_NAME`: Database name (default: "jobly")
- `CORS_ORIGINS`: Comma-separated allowed origins (default: "http://localhost:3000")
- `OPENAI_API_KEY`: OpenAI API key for embeddings (Phase 3) and LLM (Phase 5)
- `OPENAI_EMBEDDING_MODEL`: Embedding model name (default: "text-embedding-3-small")
- `EMBEDDING_PROVIDER`: Provider type (default: "openai")
- `LLM_PROVIDER`: LLM provider for interview prep (default: "openai")
- `LLM_MODEL`: LLM model for structured generation (default: "gpt-4o-mini")
- `MATCH_WEIGHT_*`: Optional scoring weights for match components
- `PACKETS_DIR`: Directory for packet file storage (default: "/tmp/jobly_packets")

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
