# Troubleshooting Guide

Common issues and solutions for Jobly setup and operation.

## Table of Contents

- [MongoDB Atlas Issues](#mongodb-atlas-issues)
- [OpenAI API Issues](#openai-api-issues)
- [Backend (API) Issues](#backend-api-issues)
- [Frontend (Web) Issues](#frontend-web-issues)
- [Local Agent Issues](#local-agent-issues)
- [LaTeX/PDF Compilation Issues](#latexpdf-compilation-issues)
- [Job Ingestion Issues](#job-ingestion-issues)
- [Matching Issues](#matching-issues)
- [Environment Variable Issues](#environment-variable-issues)

---

## MongoDB Atlas Issues

### Cannot connect to MongoDB Atlas

**Symptoms:**
- `pymongo.errors.ServerSelectionTimeoutError`
- `MongoNetworkError: connection refused`
- Backend fails to start with database errors

**Solutions:**

1. **Check connection string format:**
   ```bash
   # Correct format:
   mongodb+srv://username:password@cluster.mongodb.net/jobly?retryWrites=true&w=majority
   
   # Common mistakes:
   # - Missing password
   # - Using <password> literally instead of replacing it
   # - Wrong cluster name
   ```

2. **Verify network access:**
   - MongoDB Atlas → Network Access
   - Add your current IP address
   - Or add `0.0.0.0/0` for development (NOT for production)

3. **Check database user:**
   - MongoDB Atlas → Database Access
   - Ensure user exists with password
   - User should have "readWrite" role on database

4. **Test connection:**
   ```bash
   # Using mongosh CLI
   mongosh "mongodb+srv://cluster.mongodb.net/jobly" --username youruser
   ```

5. **Firewall/VPN issues:**
   - Disable VPN temporarily to test
   - Check corporate firewall rules
   - Try from different network

### Database user authentication failed

**Symptoms:**
- `Authentication failed`
- `MongoAuthenticationError`

**Solutions:**

1. **Check password escaping:**
   ```bash
   # If password contains special characters, URL-encode them:
   # @ → %40
   # : → %3A
   # / → %2F
   # ? → %3F
   
   # Example:
   # Password: p@ss:word
   # Encoded: p%40ss%3Aword
   ```

2. **Recreate database user:**
   - Delete old user in Atlas
   - Create new user with simple password (test)
   - Update connection string

---

## OpenAI API Issues

### Invalid API key

**Symptoms:**
- `openai.error.AuthenticationError: Incorrect API key`
- `401 Unauthorized` errors
- Matching fails with auth errors

**Solutions:**

1. **Verify API key format:**
   ```bash
   # Should start with sk-
   OPENAI_API_KEY=sk-proj-...
   # NOT sk- proj- (no space)
   ```

2. **Create new key:**
   - Visit https://platform.openai.com/api-keys
   - Create new secret key
   - Copy immediately (shown only once)
   - Update `.env` file

3. **Check account status:**
   - Verify account has credits/billing set up
   - Free tier has usage limits
   - Check usage at https://platform.openai.com/usage

### Rate limit exceeded

**Symptoms:**
- `RateLimitError: Rate limit reached`
- Matching computation fails partway through

**Solutions:**

1. **Wait and retry:**
   - Rate limits reset after a few seconds/minutes
   - Click "Recompute Matches" again

2. **Reduce batch size:**
   - Process fewer jobs at once
   - Filter jobs before computing matches

3. **Upgrade plan:**
   - Free tier: 3 requests/minute
   - Paid tier: Higher limits

### Embedding model not found

**Symptoms:**
- `Model not found` errors
- `InvalidRequestError: model does not exist`

**Solutions:**

1. **Use correct model name:**
   ```bash
   # Recommended:
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small
   
   # Also valid:
   # text-embedding-3-large
   # text-embedding-ada-002
   
   # Invalid:
   # ada-002 (missing prefix)
   # text-embedding-3 (incomplete)
   ```

---

## Backend (API) Issues

### Backend won't start

**Symptoms:**
- `ModuleNotFoundError` when starting
- `ImportError` messages
- Port already in use

**Solutions:**

1. **Install dependencies:**
   ```bash
   cd apps/api
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Check port availability:**
   ```bash
   # Check if port 8000 is in use:
   lsof -i :8000
   
   # Kill existing process:
   kill -9 <PID>
   
   # Or use different port:
   uvicorn app.main:app --reload --port 8001
   ```

3. **Verify virtual environment:**
   ```bash
   which python  # Should be in venv/
   python --version  # Should be 3.10+
   ```

4. **Check .env file exists:**
   ```bash
   ls -la apps/api/.env
   # If not found: cp .env.example .env
   ```

### CORS errors in frontend

**Symptoms:**
- `CORS policy: No 'Access-Control-Allow-Origin' header`
- Requests blocked in browser console

**Solutions:**

1. **Add frontend URL to CORS_ORIGINS:**
   ```bash
   # In apps/api/.env:
   CORS_ORIGINS=http://localhost:3000,http://localhost:3001
   ```

2. **Restart backend** after changing `.env`

3. **Check frontend API URL:**
   ```bash
   # In apps/web/.env.local:
   NEXT_PUBLIC_API_URL=http://localhost:8000
   # NOT https:// for local dev
   ```

### Profile upload fails

**Symptoms:**
- 400/500 errors when uploading CV
- "File processing failed"

**Solutions:**

1. **Check file format:**
   - Only PDF and DOCX supported
   - File size < 10MB recommended

2. **Install extraction dependencies:**
   ```bash
   pip install PyMuPDF python-docx
   ```

3. **Check file permissions:**
   - Ensure uploaded file is readable
   - Temporary directory writable

---

## Frontend (Web) Issues

### Frontend won't start

**Symptoms:**
- `npm run dev` fails
- Port 3000 already in use
- Module not found errors

**Solutions:**

1. **Install dependencies:**
   ```bash
   cd apps/web
   npm install
   ```

2. **Clear cache and reinstall:**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Use different port:**
   ```bash
   npm run dev -- -p 3001
   ```

4. **Check Node.js version:**
   ```bash
   node --version  # Should be 18+
   ```

### API connection fails

**Symptoms:**
- "Failed to fetch" errors
- API calls timeout
- Network errors in console

**Solutions:**

1. **Verify backend is running:**
   ```bash
   curl http://localhost:8000/docs
   # Should return HTML
   ```

2. **Check .env.local:**
   ```bash
   # Create if missing:
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   ```

3. **Restart frontend** after changing `.env.local`

---

## Local Agent Issues

### "Playwright browser not found"

**Symptoms:**
- `browserType.launch: Executable doesn't exist`
- Browser fails to launch

**Solutions:**

1. **Install Playwright browsers:**
   ```bash
   cd apps/local-agent
   npx playwright install chromium
   ```

2. **If still fails, install dependencies:**
   ```bash
   # macOS:
   npx playwright install-deps chromium
   
   # Linux:
   sudo npx playwright install-deps chromium
   ```

### "Invalid token" or "Token expired"

**Symptoms:**
- `401 Unauthorized` when fetching intent
- "Token has expired" message

**Solutions:**

1. **Generate new token:**
   - Tokens expire after 15 minutes
   - Go to Packet page → "Create Application" → "Open & Prefill"
   - Copy new token immediately

2. **Use token right away:**
   - Don't wait between generation and usage
   - Token is single-use and short-lived

### "API is not responding"

**Symptoms:**
- `ECONNREFUSED` errors
- Cannot reach API

**Solutions:**

1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/docs
   ```

2. **Update API_URL in .env:**
   ```bash
   # apps/local-agent/.env
   API_URL=http://localhost:8000
   ```

3. **Check firewall:**
   - Allow connections to localhost:8000

### Form fields not filling

**Symptoms:**
- Browser opens but fields stay empty
- Partial filling
- Screenshots show empty form

**Solutions:**

1. **Check ATS detection:**
   - Look at agent console output
   - Should detect ATS type (Greenhouse, Lever, etc.)
   - Generic fallback may have limited support

2. **Verify profile data:**
   - Ensure profile has required fields (name, email, phone)
   - Check packet was generated successfully

3. **Try headless=false:**
   ```bash
   # In apps/local-agent/.env
   HEADLESS=false
   ```
   - Watch browser to see what's happening

4. **Check screenshots:**
   - Look in `apps/local-agent/screenshots/`
   - See where automation stopped

### Resume not uploading

**Symptoms:**
- Form fills but no resume attached
- File upload field empty

**Solutions:**

1. **Verify PDF exists:**
   ```bash
   # Check packet directory
   ls -la /tmp/jobly_packets/<packet_id>/
   # Should see cv.pdf
   ```

2. **Check file path:**
   - Agent needs access to packet directory
   - File permissions should allow read

3. **LaTeX compilation:**
   - If no PDF, check if LaTeX is installed
   - .tex file will be there but not .pdf

---

## LaTeX/PDF Compilation Issues

### PDFs not generating

**Symptoms:**
- Only .tex files available for download
- No PDF option in packet view
- "PDF compilation not available"

**Solutions:**

1. **Install LaTeX:**

   **macOS:**
   ```bash
   brew install --cask mactex
   # Or lighter version:
   brew install --cask basictex
   ```

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install texlive-latex-base texlive-latex-extra latexmk
   ```

2. **Verify installation:**
   ```bash
   which latexmk  # Should return path
   latexmk --version
   ```

3. **Restart backend** after installing LaTeX

4. **Alternative - Compile locally:**
   - Download .tex file
   - Upload to Overleaf.com
   - Or compile locally: `latexmk -pdf cv.tex`

### LaTeX compilation errors

**Symptoms:**
- PDF generation fails with errors
- Compilation logs show errors

**Solutions:**

1. **Check LaTeX packages:**
   ```bash
   # Install full distribution:
   sudo apt-get install texlive-full  # Linux
   brew install --cask mactex  # macOS
   ```

2. **Review .tex file:**
   - Download .tex
   - Try compiling manually to see error
   - Report issue if template is broken

---

## Job Ingestion Issues

### No jobs appearing after ingestion

**Symptoms:**
- Ingestion completes but job list is empty
- "0 new jobs" message

**Solutions:**

1. **Check enabled sources:**
   ```bash
   # In apps/api/job_sources_config.yaml
   # Ensure at least one source has:
   enabled: true
   ```

2. **Verify RSS feed URLs:**
   ```bash
   # Test manually:
   curl -I https://remoteok.com/remote-dev-jobs.rss
   # Should return 200 OK
   ```

3. **Check logs:**
   - Look for error messages during ingestion
   - May be rate limited or blocked

4. **Test with simple source:**
   ```yaml
   - name: "RemoteOK RSS"
     type: "rss"
     enabled: true
     url: "https://remoteok.com/remote-dev-jobs.rss"
     compliance_note: "Public RSS feed"
     rate_limit_seconds: 60
   ```

### Duplicate jobs appearing

**Symptoms:**
- Same job listed multiple times
- Deduplication not working

**Solutions:**

1. **Check dedupe_hash:**
   - Should be unique per job
   - Based on company + title + url

2. **Clear and re-ingest:**
   ```bash
   # In MongoDB, delete jobs collection
   # Then re-run ingestion
   ```

3. **Report issue** if deduplication is truly broken

---

## Matching Issues

### "No embeddings available"

**Symptoms:**
- Match computation fails
- "Profile has no embedding" error

**Solutions:**

1. **Verify OpenAI key:**
   ```bash
   # In apps/api/.env
   OPENAI_API_KEY=sk-...
   ```

2. **Recompute from scratch:**
   - Delete matches collection in MongoDB
   - Click "Recompute Matches" again

3. **Check profile exists:**
   - Ensure profile is saved
   - Profile should have skills and experience

### Match scores all 0 or very low

**Symptoms:**
- All matches have score near 0
- No good matches found

**Solutions:**

1. **Update profile:**
   - Add more skills
   - Add detailed experience
   - Set preferences

2. **Check job descriptions:**
   - Jobs need description text
   - Empty descriptions = poor matches

3. **Adjust weights:**
   ```bash
   # In apps/api/.env
   MATCH_WEIGHT_SEMANTIC=0.5  # Increase semantic weight
   ```

---

## Environment Variable Issues

### Changes to .env not taking effect

**Symptoms:**
- Updated .env but behavior unchanged
- Old values still being used

**Solutions:**

1. **Restart application:**
   - Backend: Stop and restart `uvicorn`
   - Frontend: Stop (Ctrl+C) and `npm run dev`
   - Local agent: No restart needed (reads per-run)

2. **Check correct .env file:**
   - Backend: `apps/api/.env`
   - Frontend: `apps/web/.env.local`
   - Local agent: `apps/local-agent/.env`

3. **Verify .env syntax:**
   ```bash
   # Correct:
   OPENAI_API_KEY=sk-abc123
   
   # Wrong:
   OPENAI_API_KEY = sk-abc123  # No spaces
   OPENAI_API_KEY="sk-abc123"  # No quotes needed
   ```

### "Environment variable not set" errors

**Symptoms:**
- Application complains about missing variables
- KeyError for environment variable

**Solutions:**

1. **Create .env from example:**
   ```bash
   cp .env.example .env
   # Then edit .env with your values
   ```

2. **Check required variables:**
   - `MONGODB_URI` - always required
   - `OPENAI_API_KEY` - required for Phase 3+

---

## Getting More Help

If you're still stuck:

1. **Check logs:**
   - Backend: Terminal running `uvicorn`
   - Frontend: Browser console (F12)
   - Local agent: Terminal output

2. **Enable debug mode:**
   ```bash
   # Backend - add to .env:
   LOG_LEVEL=DEBUG
   ```

3. **Test minimal setup:**
   - Start fresh with just backend + database
   - Add features one at a time

4. **Open GitHub issue:**
   - Include error messages
   - Include relevant config (remove secrets!)
   - Describe steps to reproduce

5. **Check documentation:**
   - [QUICKSTART.md](./QUICKSTART.md)
   - [ENVIRONMENT.md](./ENVIRONMENT.md)
   - [LEGAL_COMPLIANCE.md](./LEGAL_COMPLIANCE.md)
