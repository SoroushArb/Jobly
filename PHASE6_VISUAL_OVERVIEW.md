# Phase 6: Visual Architecture Overview

## System Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                         USER WORKFLOW                                 │
│                                                                       │
│  1. Generate Packet  →  2. Click "Open & Prefill"  →  3. Run Agent  │
│     (from Matches)        (creates intent + token)      (in terminal) │
│                                                                       │
│  6. Mark Applied  ←  5. Review & Submit  ←  4. Browser Opens         │
│     (in UI)           (manually)              (auto-fills form)       │
└───────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                      COMPONENT ARCHITECTURE                           │
└───────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│       Jobly Web UI (Next.js/React)      │
│  ┌─────────────────────────────────┐   │
│  │  Packet Detail Page             │   │
│  │  - "Open & Prefill" button      │   │
│  │  - Intent modal with CLI cmd    │   │
│  │  - Token display (once!)        │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Applications Page              │   │
│  │  - Status tracking table        │   │
│  │  - Filter by status             │   │
│  │  - Update status actions        │   │
│  └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │
               │ HTTPS REST API
               ▼
┌─────────────────────────────────────────┐
│     Jobly API (FastAPI/Python)          │
│  ┌─────────────────────────────────┐   │
│  │  Applications Router            │   │
│  │  - POST /applications/create    │   │
│  │  - GET /applications            │   │
│  │  - PATCH /.../status            │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Prefill Router                 │   │
│  │  - POST /prefill/create-intent  │   │
│  │  - GET /prefill/intent/{id}     │   │
│  │  - POST /prefill/report-result  │   │
│  └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │
               │ Motor (Async MongoDB Driver)
               ▼
┌─────────────────────────────────────────┐
│        MongoDB Atlas (Cloud)            │
│  ┌─────────────────────────────────┐   │
│  │  applications                   │   │
│  │  - status tracking              │   │
│  │  - status_history               │   │
│  │  - links to packet/intent/log   │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  prefill_intents                │   │
│  │  - job_url, user_fields         │   │
│  │  - auth_token (hashed)          │   │
│  │  - token_expires_at             │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  prefill_logs                   │   │
│  │  - filled_fields, errors        │   │
│  │  - screenshot_paths             │   │
│  │  - detected_ats                 │   │
│  └─────────────────────────────────┘   │
└──────────────▲──────────────────────────┘
               │
               │ HTTPS + Bearer Token
               │
┌──────────────┴──────────────────────────┐
│   Local Agent (Node.js/TypeScript)      │
│   ┌─────────────────────────────────┐  │
│   │  Main Service                   │  │
│   │  - Fetches intent from API      │  │
│   │  - Launches Playwright browser  │  │
│   │  - Orchestrates filling         │  │
│   │  - Reports results to API       │  │
│   └─────────────┬───────────────────┘  │
│                 │                       │
│   ┌─────────────▼───────────────────┐  │
│   │  Adapter Factory                │  │
│   │  - Tries all adapters           │  │
│   │  - Selects highest confidence   │  │
│   └─────────────┬───────────────────┘  │
│                 │                       │
│   ┌─────────────▼───────────────────┐  │
│   │  ATS Adapters                   │  │
│   │  ┌─────────────────────────┐    │  │
│   │  │ Greenhouse (✅)         │    │  │
│   │  │ - boards.greenhouse.io  │    │  │
│   │  │ - #first_name, #email   │    │  │
│   │  └─────────────────────────┘    │  │
│   │  ┌─────────────────────────┐    │  │
│   │  │ Lever (✅)              │    │  │
│   │  │ - jobs.lever.co         │    │  │
│   │  │ - [name="email"]        │    │  │
│   │  └─────────────────────────┘    │  │
│   │  ┌─────────────────────────┐    │  │
│   │  │ Generic (✅)            │    │  │
│   │  │ - Smart label detection │    │  │
│   │  │ - Flexible selectors    │    │  │
│   │  └─────────────────────────┘    │  │
│   │  ┌─────────────────────────┐    │  │
│   │  │ Workday (🚧)            │    │  │
│   │  │ - Detection only        │    │  │
│   │  └─────────────────────────┘    │  │
│   │  ┌─────────────────────────┐    │  │
│   │  │ LinkedIn (🚧)           │    │  │
│   │  │ - Detection only        │    │  │
│   │  └─────────────────────────┘    │  │
│   └─────────────────────────────────┘  │
└──────────────┬──────────────────────────┘
               │
               │ Playwright API
               ▼
┌─────────────────────────────────────────┐
│       Chromium Browser (Local)          │
│  - Navigates to job application page    │
│  - Fills form fields                    │
│  - Uploads resume file                  │
│  - Takes screenshots                    │
│  - Stops before submit                  │
└─────────────────────────────────────────┘
```

## Data Flow

### 1. Intent Creation Flow

```
User clicks           Web UI sends          API generates        API stores
"Open & Prefill"  →   POST request     →    token + intent  →    in MongoDB
                                             (15 min TTL)         (hashed token)
                                                 │
                                                 ▼
                                            Returns to UI:
                                            - intent_id
                                            - auth_token (plain)
                                            - expires_at
```

### 2. Local Agent Execution Flow

```
User runs CLI     Agent fetches      Agent launches    Adapter detects
with token    →   intent from API →  browser       →   ATS type
                  (validates token)   (Playwright)      (confidence)
                        │                                     │
                        ▼                                     ▼
                  Returns:                              Selects best
                  - job_url                             adapter
                  - user_fields                              │
                  - attachments                              ▼
                                                        Fills form +
                                                        uploads resume
                                                             │
                                                             ▼
                                                        Takes screenshots
                                                             │
                                                             ▼
                                                        STOPS before submit
                                                             │
                                                             ▼
                                                        Reports results
                                                        to API
```

### 3. Result Reporting Flow

```
Agent posts        API validates      API saves         API updates
PrefillLog    →    auth token     →   log to        →   application
to /report-result  (checks expiry)    MongoDB           status to
                                                         "prefilled"
```

## Security Model

```
┌─────────────────────────────────────────┐
│         Token Lifecycle                 │
└─────────────────────────────────────────┘

1. Generation
   └─→ secrets.token_urlsafe(32)
       └─→ 256-bit random token

2. Storage
   └─→ SHA256 hash only
       └─→ Never store plain token

3. Display
   └─→ Shown ONCE in UI
       └─→ Copy immediately!

4. Usage
   └─→ Bearer token in HTTP header
       └─→ Validated against hash

5. Expiry
   └─→ 15 minutes from creation
       └─→ Rejected after expiry

6. Scope
   └─→ Single intent only
       └─→ Can't reuse for different intent
```

## Canonical Field Mapping

```
┌────────────────────┬─────────────────────────────────────┐
│ Canonical Field    │ Example Selectors                   │
├────────────────────┼─────────────────────────────────────┤
│ name               │ #first_name, [name="name"]          │
│ surname            │ #last_name, [name="last_name"]      │
│ email              │ #email, input[type="email"]         │
│ phone              │ #phone, input[type="tel"]           │
│ linkedin           │ [name*="linkedin"], #linkedin       │
│ github             │ [name*="github"], #github           │
│ location_city      │ [name*="city"], #city               │
│ location_country   │ [name*="country"], #country         │
│ resume             │ input[type="file"], #resume         │
└────────────────────┴─────────────────────────────────────┘

Selection Strategy:
1. Try ATS-specific selectors (Greenhouse: #first_name)
2. Try common name patterns ([name="name"])
3. Try label text matching (label:has-text("Email"))
4. Try placeholder matching ([placeholder*="Email"])
5. Try aria-label matching ([aria-label*="Email"])
```

## Application Status Pipeline

```
┌──────────┐
│ prepared │  ← Packet generated, ready to apply
└────┬─────┘
     │
     ▼
┌────────────────┐
│ intent_created │  ← Prefill intent generated with token
└────┬───────────┘
     │
     ▼
┌────────────┐
│ prefilling │  ← (Optional) Agent is currently running
└────┬───────┘
     │
     ▼
┌───────────┐
│ prefilled │  ← Form filled, waiting for user to submit
└────┬──────┘
     │
     ▼
┌─────────┐
│ applied │  ← User confirmed submission
└────┬────┘
     │
     ├──→ rejected
     │
     ├──→ interviewing
     │     └──→ offered
     │           ├──→ accepted
     │           └──→ declined
     │
     └──→ withdrawn
```

## File Structure Tree

```
Jobly/
├── apps/
│   ├── api/                          # FastAPI Backend
│   │   ├── app/
│   │   │   ├── routers/
│   │   │   │   ├── applications.py   # ✨ NEW: Application CRUD
│   │   │   │   └── prefill.py        # ✨ NEW: Intent & reporting
│   │   │   ├── schemas/
│   │   │   │   └── application.py    # ✨ NEW: Pydantic models
│   │   │   └── models/
│   │   │       └── database.py       # ✨ UPDATED: New collections
│   │   └── tests/
│   │       └── test_applications.py  # ✨ NEW: Schema tests
│   │
│   ├── local-agent/                  # ✨ NEW: Playwright Agent
│   │   ├── src/
│   │   │   ├── adapters/
│   │   │   │   ├── base.ts           # Interface
│   │   │   │   ├── greenhouse.ts     # Greenhouse ATS
│   │   │   │   ├── lever.ts          # Lever ATS
│   │   │   │   ├── generic.ts        # Fallback
│   │   │   │   ├── workday.ts        # Scaffold
│   │   │   │   ├── linkedin.ts       # Scaffold
│   │   │   │   └── index.ts          # Factory
│   │   │   ├── utils/
│   │   │   │   ├── api-client.ts     # API communication
│   │   │   │   └── prefill-service.ts # Main orchestrator
│   │   │   └── index.ts              # CLI entry point
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── README.md                 # Setup guide
│   │
│   └── web/                          # Next.js Frontend
│       ├── app/
│       │   ├── applications/
│       │   │   └── page.tsx          # ✨ NEW: Status tracker
│       │   └── packets/[id]/
│       │       └── page.tsx          # ✨ UPDATED: Prefill button
│       ├── lib/
│       │   └── api.ts                # ✨ UPDATED: New API methods
│       └── types/
│           └── application.ts        # ✨ NEW: TypeScript types
│
├── PHASE6_IMPLEMENTATION.md          # ✨ NEW: Full tech guide
├── PHASE6_SUMMARY.md                 # ✨ NEW: Quick reference
├── PHASE6_VISUAL_OVERVIEW.md         # ✨ NEW: This file
└── README.md                         # ✨ UPDATED: Phase 6 info
```

Legend:
- ✨ NEW: Completely new file
- ✨ UPDATED: Modified existing file

## Statistics

```
┌─────────────────────────┬──────────┐
│ Metric                  │ Count    │
├─────────────────────────┼──────────┤
│ Total Files Added       │ 24       │
│ Total Files Modified    │ 6        │
│ Lines of Code (Backend) │ ~650     │
│ Lines of Code (Agent)   │ ~800     │
│ Lines of Code (Frontend)│ ~750     │
│ Documentation Lines     │ ~1,000   │
├─────────────────────────┼──────────┤
│ Total Lines Added       │ ~3,200   │
└─────────────────────────┴──────────┘

Backend Components:
- 2 new routers (applications, prefill)
- 1 new schema module (application)
- 3 database helpers (collections)
- 1 test module (9 tests)

Local Agent Components:
- 5 ATS adapters (2 complete, 3 scaffolds)
- 1 adapter factory
- 2 utility modules (API client, service)
- 1 CLI entry point

Frontend Components:
- 1 new page (applications)
- 1 updated page (packets detail)
- 1 new types module
- 1 updated API client
```

## Quick Reference

### For Developers

**Adding a new ATS adapter:**
1. Create `apps/local-agent/src/adapters/myats.ts`
2. Extend `ATSAdapter` class
3. Implement: `detect()`, `collectFields()`, `fill()`, `attachResume()`
4. Add to `AdapterFactory` in `index.ts`
5. Test with real job posting URL

**Testing the system:**
1. Start backend: `cd apps/api && uvicorn app.main:app --reload`
2. Start frontend: `cd apps/web && npm run dev`
3. Generate packet from matches page
4. Click "Open & Prefill" on packet page
5. Copy displayed command
6. Run: `cd apps/local-agent && <paste command>`
7. Watch browser automation
8. Review filled form
9. Submit manually
10. Update status in UI

### For Users

**First-time setup:**
```bash
# Install local agent
cd apps/local-agent
npm install
npx playwright install chromium
```

**Each time you apply:**
```bash
# 1. Generate packet (in web UI)
# 2. Click "Open & Prefill" (in web UI)
# 3. Run agent (in terminal)
cd apps/local-agent
npm run dev -- <intent_id> <auth_token>
# 4. Review form in browser
# 5. Submit manually
# 6. Update status (in web UI)
```

## Security Checklist

- ✅ Tokens expire after 15 minutes
- ✅ Tokens stored as SHA256 hash only
- ✅ Tokens shown only once in UI
- ✅ Authorization required for intent fetch
- ✅ Token validation on every request
- ✅ No passwords stored anywhere
- ✅ Local execution only (no cloud)
- ✅ HTTPS required for production
- ✅ Always stops before submit
- ✅ Screenshot evidence captured
