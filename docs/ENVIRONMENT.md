# Environment Variables Reference

Complete guide to all environment variables used in Jobly.

## Backend (`apps/api/.env`)

### Required Variables

#### Database Configuration
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/jobly?retryWrites=true&w=majority
```
- **Description**: MongoDB connection string
- **Required**: Yes
- **Default**: None
- **Where to get**: MongoDB Atlas dashboard → Connect → Connect your application
- **Used in**: All phases for data persistence

```bash
MONGODB_DB_NAME=jobly
```
- **Description**: Database name in MongoDB
- **Required**: No
- **Default**: `jobly`
- **Used in**: All phases

#### OpenAI Configuration (Required for Phases 3 & 5)
```bash
OPENAI_API_KEY=sk-your_openai_api_key_here
```
- **Description**: OpenAI API key for embeddings and LLM
- **Required**: Yes (for Phase 3 matching and Phase 5 interview prep)
- **Default**: None
- **Where to get**: https://platform.openai.com/api-keys
- **Used in**: 
  - Phase 3: Semantic job matching with embeddings
  - Phase 5: Interview preparation content generation

```bash
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```
- **Description**: OpenAI embedding model name
- **Required**: No
- **Default**: `text-embedding-3-small`
- **Options**: `text-embedding-3-small`, `text-embedding-3-large`, `text-embedding-ada-002`
- **Used in**: Phase 3 matching

```bash
EMBEDDING_PROVIDER=openai
```
- **Description**: Embedding provider type
- **Required**: No
- **Default**: `openai`
- **Options**: `openai` (others can be added via provider abstraction)
- **Used in**: Phase 3 matching

### LLM Configuration (Phase 5)
```bash
LLM_PROVIDER=openai
```
- **Description**: LLM provider for interview generation
- **Required**: No
- **Default**: `openai`
- **Options**: `openai` (swappable architecture)
- **Used in**: Phase 5 interview prep

```bash
LLM_MODEL=gpt-4o-mini
```
- **Description**: LLM model for structured generation
- **Required**: No
- **Default**: `gpt-4o-mini`
- **Options**: `gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo`, etc.
- **Used in**: Phase 5 interview prep

### CORS Configuration
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```
- **Description**: Comma-separated allowed CORS origins
- **Required**: No
- **Default**: `http://localhost:3000`
- **Used in**: API CORS middleware

### Optional: Match Scoring Weights (Phase 3)

All weights are optional and have sensible defaults. Values should be between 0 and 1 and will be normalized.

```bash
MATCH_WEIGHT_SEMANTIC=0.35
```
- **Description**: Weight for semantic similarity (embedding-based)
- **Default**: `0.35`
- **Range**: `0.0` to `1.0`

```bash
MATCH_WEIGHT_SKILL_OVERLAP=0.25
```
- **Description**: Weight for skill overlap analysis
- **Default**: `0.25`
- **Range**: `0.0` to `1.0`

```bash
MATCH_WEIGHT_SENIORITY_FIT=0.15
```
- **Description**: Weight for seniority level matching
- **Default**: `0.15`
- **Range**: `0.0` to `1.0`

```bash
MATCH_WEIGHT_LOCATION_FIT=0.15
```
- **Description**: Weight for location preference alignment
- **Default**: `0.15`
- **Range**: `0.0` to `1.0`

```bash
MATCH_WEIGHT_RECENCY=0.10
```
- **Description**: Weight for job posting recency
- **Default**: `0.10`
- **Range**: `0.0` to `1.0`

### Packet Storage (Phase 4)
```bash
PACKETS_DIR=/tmp/jobly_packets
```
- **Description**: Directory for storing generated application packets
- **Required**: No
- **Default**: `/tmp/jobly_packets`
- **Note**: Directory will be created automatically if it doesn't exist
- **Used in**: Phase 4 CV/packet generation

## Frontend (`apps/web/.env.local`)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```
- **Description**: Backend API base URL
- **Required**: No
- **Default**: `http://localhost:8000`
- **Production**: Set to your deployed backend URL
- **Used in**: All API calls from the frontend

## Local Agent (`apps/local-agent/.env`)

### API Configuration
```bash
API_URL=http://localhost:8000
```
- **Description**: Backend API URL for fetching prefill intents
- **Required**: No
- **Default**: `http://localhost:8000`
- **Production**: Set to your deployed backend URL
- **Used in**: Fetching prefill intents and reporting results

```bash
POLLING_INTERVAL_MS=5000
```
- **Description**: Polling interval in milliseconds (not used in manual mode)
- **Required**: No
- **Default**: `5000`
- **Note**: Currently not used (manual invocation mode)

### Browser Configuration
```bash
HEADLESS=false
```
- **Description**: Run browser in headless mode
- **Required**: No
- **Default**: `false`
- **Options**: `true` (headless), `false` (visible browser)
- **Note**: Set to `false` to watch automation, `true` for server deployment

```bash
SCREENSHOTS_DIR=./screenshots
```
- **Description**: Directory for saving automation screenshots
- **Required**: No
- **Default**: `./screenshots`
- **Note**: Directory will be created automatically

### Safety Configuration
```bash
STOP_BEFORE_SUBMIT=true
```
- **Description**: Stop automation before final form submission
- **Required**: No
- **Default**: `true`
- **Recommendation**: **Keep as `true`** for safety - allows manual review before submission
- **Warning**: Setting to `false` will auto-submit applications (not recommended)

## Environment Variable Checklist

### Minimal Setup (Phase 1-2)
- [x] `MONGODB_URI` (required)
- [x] `MONGODB_DB_NAME` (optional, defaults to "jobly")

### With AI Matching (Phase 3)
- [x] `MONGODB_URI` (required)
- [x] `OPENAI_API_KEY` (required)
- [x] `OPENAI_EMBEDDING_MODEL` (optional)
- [x] `EMBEDDING_PROVIDER` (optional)

### With Interview Prep (Phase 5)
- [x] All Phase 3 variables
- [x] `LLM_PROVIDER` (optional)
- [x] `LLM_MODEL` (optional)

### With Application Automation (Phase 6)
- [x] Local agent: `API_URL` (optional)
- [x] Local agent: `STOP_BEFORE_SUBMIT` (recommended: true)

## Production Deployment

For production deployment, update:

**Backend:**
- `CORS_ORIGINS`: Add your production frontend URL
- `PACKETS_DIR`: Use a persistent volume path

**Frontend:**
- `NEXT_PUBLIC_API_URL`: Your production backend URL

**Local Agent:**
- `API_URL`: Your production backend URL
- `HEADLESS`: Consider `true` for server deployment (if applicable)

## Secrets Management

**Important**: Never commit `.env` files to version control!

For production:
- Use environment variable managers (e.g., AWS Secrets Manager, Vercel Environment Variables)
- Rotate API keys regularly
- Use separate OpenAI keys for dev/prod
- Restrict MongoDB network access to known IPs

## Validation

To verify your environment setup:

1. **Backend**: Visit http://localhost:8000/docs - should load without errors
2. **Frontend**: Visit http://localhost:3000 - should connect to backend
3. **Local Agent**: Run with test intent - browser should launch

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common configuration issues.
