# Jobly Quickstart Guide

Get Jobly up and running in minutes with MongoDB Atlas (recommended).

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **MongoDB Atlas account** (free tier works great)
- **OpenAI API key** (for AI-powered matching and interview prep)

## Step 1: Clone the Repository

```bash
git clone https://github.com/SoroushArb/Jobly.git
cd Jobly
```

## Step 2: Set Up MongoDB Atlas

1. **Create Account**: Sign up at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. **Create Cluster**: 
   - Choose free M0 tier
   - Select your preferred region
   - Create cluster (takes ~3-5 minutes)
3. **Configure Access**:
   - **Database Access**: Create a database user with password
   - **Network Access**: Add your IP address (or `0.0.0.0/0` for development)
4. **Get Connection String**:
   - Click "Connect" → "Connect your application"
   - Copy the connection string (looks like `mongodb+srv://...`)
   - Replace `<password>` with your database user password

## Step 3: Set Up the Backend (API)

```bash
cd apps/api

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

Edit `.env` and set:
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/jobly?retryWrites=true&w=majority
OPENAI_API_KEY=sk-your_openai_api_key_here
```

Start the backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend running at http://localhost:8000 (docs at http://localhost:8000/docs)

## Step 4: Set Up the Frontend (Web)

Open a new terminal:

```bash
cd apps/web

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# (defaults should work for local development)

# Start the frontend
npm run dev
```

✅ Frontend running at http://localhost:3000

## Step 5: Upload Your Profile

1. Visit http://localhost:3000/profile
2. Upload your CV (PDF or DOCX)
3. Review and edit the auto-extracted profile
4. Set your job preferences (location, remote, skills, roles)
5. Click "Save Profile"

## Step 6: Ingest Jobs

1. Visit http://localhost:3000/jobs
2. Click "Trigger Job Ingestion" to fetch jobs from configured sources
3. Wait for ingestion to complete (~30 seconds)
4. Browse available jobs with filters

## Step 7: Compute Matches

1. Visit http://localhost:3000/matches
2. Click "Recompute Matches" to get AI-powered job recommendations
3. Browse ranked matches with match scores
4. Click "View Details" to see why jobs match and what gaps exist

## Step 8: Generate Application Packet

1. From the Matches page, click "Generate Packet" for a job
2. View the tailored CV, cover letter, and application materials
3. Download the files (LaTeX .tex always available, PDF if LaTeX installed)

## Step 9: Prepare for Interview

1. From the Packet page, click "Prepare Interview"
2. Review AI-generated interview materials:
   - 30/60/90 day plan
   - STAR stories based on your experience
   - Technical Q&A for your skill gaps
   - Questions to ask the interviewer
3. Export as Markdown for offline study

## Step 10: Automate Application (Optional)

Set up the local agent for browser automation:

```bash
cd apps/local-agent

# Install dependencies
npm install

# Install Playwright browsers
npx playwright install chromium

# Configure environment
cp .env.example .env
```

From the Packet page:
1. Click "Create Application"
2. Click "Open & Prefill" to generate a token
3. Copy the command and run it in terminal
4. Watch the browser automatically fill the application form
5. Review and manually submit when satisfied

## Next Steps

- **Configure Job Sources**: Edit `apps/api/job_sources_config.yaml` to add/remove sources
- **Customize Matching**: Adjust weights in `.env` under `MATCH_WEIGHT_*`
- **Install LaTeX** (optional): For PDF CV generation - see [main README](../README.md#pdf-compilation-optional)
- **Track Applications**: Use the Applications page to manage your pipeline

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues.

## Environment Variables

See [ENVIRONMENT.md](./ENVIRONMENT.md) for complete environment variable reference.

## Legal & Compliance

See [LEGAL_COMPLIANCE.md](./LEGAL_COMPLIANCE.md) for job source compliance guidance.
