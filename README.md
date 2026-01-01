# Jobly

AI Job Hunter Agent - Phase 1: User Profile Intake

A comprehensive job hunting platform that helps you manage your professional profile and job search preferences.

## 🚀 Features

- **CV Upload & Parsing**: Upload PDF/DOCX files and automatically extract structured profile data
- **Profile Management**: Create, edit, and manage your professional profile
- **Job Preferences**: Set location, language, skill, and role preferences
- **Evidence Tracking**: See where each piece of information came from in your CV
- **MongoDB Storage**: Persistent storage with MongoDB Atlas

## 📁 Project Structure

This is a monorepo containing:

- **`apps/api`**: FastAPI backend for CV processing and profile management
- **`apps/web`**: Next.js frontend for profile management UI

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

1. **Upload CV**: Visit http://localhost:3000/profile and upload your CV (PDF or DOCX)
2. **Review Extracted Data**: See the raw extracted text and auto-populated profile
3. **Edit Profile**: Update your name, email, skills, experience, and other details
4. **Set Preferences**: Configure your job search preferences (location, remote, skills, etc.)
5. **Save**: Save your profile to MongoDB for persistence

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

- `POST /profile/upload-cv`: Upload and parse CV
- `POST /profile/save`: Save profile to database
- `GET /profile`: Retrieve saved profile
- `PATCH /profile`: Update profile fields

See [apps/api/README.md](apps/api/README.md) for detailed API documentation.

## 📝 Example Profile

See [apps/api/example_seed_profile.json](apps/api/example_seed_profile.json) for a complete example profile structure.

## 🔒 Environment Variables

### Backend (apps/api/.env)
- `MONGODB_URI`: MongoDB connection string
- `MONGODB_DB_NAME`: Database name (default: "jobly")
- `CORS_ORIGINS`: Comma-separated allowed origins (default: "http://localhost:3000")

### Frontend (apps/web/.env.local)
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: "http://localhost:8000")

## 🤝 Contributing

This is Phase 1 of the AI Job Hunter Agent. Future phases will include:
- Job discovery and scraping
- AI-powered job matching
- Resume tailoring
- Application tracking

## 📄 License

MIT

## 🎯 Phase 1 Acceptance Criteria

✅ CV upload (PDF/DOCX) with text extraction  
✅ Schema-valid UserProfile draft generation  
✅ MongoDB Atlas integration  
✅ Editable profile screen in Next.js  
✅ Preferences editor (location, skills, roles)  
✅ Save and reload profile functionality  
✅ Evidence tracking for extracted data  
✅ Pydantic v2 validation  
✅ FastAPI endpoints with CORS  
✅ Basic unit tests
