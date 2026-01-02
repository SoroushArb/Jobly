# Jobly Local Agent - Prefill Assistant

A local Playwright-based service that automates job application form filling while maintaining security and user control.

## Overview

The Local Agent runs on your macOS machine and communicates securely with the Jobly API to:
- Fetch prefill intents (job application data)
- Launch a real browser session
- Detect ATS type (Greenhouse, Lever, Workday, LinkedIn, or generic)
- Prefill form fields with your profile data
- Attach your tailored CV PDF
- Take screenshots of the process
- Stop before final submission (for safety)
- Report results back to the API

## Architecture

```
┌─────────────────┐         HTTPS + Token        ┌─────────────────┐
│   Jobly API     │◄─────────────────────────────│  Local Agent    │
│   (Cloud)       │                               │   (Your Mac)    │
└─────────────────┘                               └─────────────────┘
         │                                                  │
         │                                                  │
    MongoDB                                          Real Browser
  (Applications,                                    (Playwright)
   Intents, Logs)
```

**Security Model:**
- Short-lived tokens (15 min expiry)
- HTTPS communication
- No passwords stored
- Local execution only

## Prerequisites

- macOS 10.15+
- Node.js 18+
- npm or yarn
- Internet connection

## Installation

1. Navigate to the local agent directory:
```bash
cd apps/local-agent
```

2. Install dependencies:
```bash
npm install
```

3. Install Playwright browsers:
```bash
npx playwright install chromium
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env if needed (defaults should work)
```

## Configuration

Edit `.env` to customize settings:

```bash
# API Configuration
API_URL=http://localhost:8000          # Backend API URL
POLLING_INTERVAL_MS=5000               # Not used in manual mode

# Browser Configuration
HEADLESS=false                          # Set to true for headless mode
SCREENSHOTS_DIR=./screenshots          # Where to save screenshots

# Safety
STOP_BEFORE_SUBMIT=true                # Always stop before submitting (RECOMMENDED)
```

## Usage

### Step 1: Create Application in Web UI

1. Go to your Jobly web app (http://localhost:3000)
2. Navigate to a packet detail page
3. Click "Create Application"

### Step 2: Generate Prefill Intent

From the application view, click "Open & Prefill" to generate a prefill intent. The UI will display:
- Intent ID
- Auth Token (shown only once!)
- Expiry timestamp

**Important:** Copy both the Intent ID and Auth Token immediately.

### Step 3: Run Local Agent

Execute the agent with the intent ID and token:

```bash
npm run dev -- <intent_id> <auth_token>
```

Example:
```bash
npm run dev -- 507f1f77bcf86cd799439011 abcdef123456789token
```

### What Happens Next

1. **Browser Launch**: A Chromium browser window opens
2. **Navigation**: Navigates to the job application URL
3. **ATS Detection**: Identifies the application system (Greenhouse, Lever, etc.)
4. **Form Filling**: Fills in your name, email, phone, LinkedIn, etc.
5. **Resume Upload**: Attaches your tailored CV PDF
6. **Screenshots**: Takes screenshots at each step
7. **Report Back**: Sends results to API
8. **Pause**: Browser remains open for 10 seconds for review
9. **Stop**: Process completes without submitting

### Step 4: Review in Web UI

Return to the web UI to see:
- Screenshots from the prefill
- Fields that were filled successfully
- Any errors or missing fields
- Application status updated to "Prefilled"

### Step 5: Manual Submit (You Control This)

The agent stops before submitting. You should:
1. Review the filled form
2. Correct any errors
3. Answer any custom questions
4. Click submit manually when ready
5. Update application status in UI to "Applied"

## ATS Support

### ✅ Fully Implemented
- **Greenhouse**: boards.greenhouse.io, grnh.se
- **Lever**: jobs.lever.co
- **Generic**: Fallback for custom forms

### 🚧 Detection Only (TODO)
- **Workday**: myworkdayjobs.com
- **LinkedIn**: linkedin.com/jobs (Easy Apply)

## Supported Fields

The agent can fill the following canonical fields:

- `name` - First name
- `surname` - Last name
- `email` - Email address
- `phone` - Phone number
- `linkedin` - LinkedIn profile URL
- `github` - GitHub profile URL
- `location_city` - City
- `location_country` - Country

Additional fields can be added via the adapter implementations.

## File Structure

```
apps/local-agent/
├── src/
│   ├── adapters/           # ATS adapters
│   │   ├── base.ts         # Base adapter interface
│   │   ├── greenhouse.ts   # Greenhouse implementation
│   │   ├── lever.ts        # Lever implementation
│   │   ├── workday.ts      # Workday scaffold
│   │   ├── linkedin.ts     # LinkedIn scaffold
│   │   ├── generic.ts      # Generic fallback
│   │   └── index.ts        # Adapter factory
│   ├── utils/
│   │   ├── api-client.ts   # API communication
│   │   └── prefill-service.ts  # Main prefill logic
│   └── index.ts            # Entry point
├── screenshots/            # Generated screenshots
├── package.json
├── tsconfig.json
└── .env                    # Configuration
```

## Troubleshooting

### "API is not responding"
- Ensure the backend is running: `cd apps/api && uvicorn app.main:app --reload`
- Check API_URL in .env matches your backend

### "Invalid token" or "Token expired"
- Tokens expire after 15 minutes
- Generate a new intent from the web UI
- Use the new token immediately

### "Browser not found"
- Run: `npx playwright install chromium`

### Fields not filling correctly
- Check screenshots in `./screenshots/` to see what happened
- Different ATS may have different field patterns
- You can extend adapters in `src/adapters/` for custom forms

### Resume not uploading
- Ensure the CV PDF exists in the packet
- Check file path in the intent
- Verify file permissions

## Development

### Build TypeScript
```bash
npm run build
```

### Run built version
```bash
npm start -- <intent_id> <auth_token>
```

### Add a new adapter

1. Create `src/adapters/myats.ts`
2. Extend `ATSAdapter`
3. Implement `detect()`, `collectFields()`, `fill()`, `attachResume()`
4. Add to `AdapterFactory` in `src/adapters/index.ts`

## Security Considerations

✅ **Safe:**
- Tokens expire after 15 minutes
- No passwords stored anywhere
- Local execution (no cloud automation)
- Stops before submission
- HTTPS communication

❌ **Never:**
- Share auth tokens
- Run with `STOP_BEFORE_SUBMIT=false` (unless you're sure)
- Use on public/shared computers

## License

MIT
