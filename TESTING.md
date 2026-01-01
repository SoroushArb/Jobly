# Testing Guide

## Running Tests

### Backend Unit Tests

The backend includes unit tests for schemas and CV extraction logic.

```bash
cd apps/api
source venv/bin/activate
pytest -v
```

Expected output: All 14 tests should pass.

### Backend Integration Tests

Integration tests verify the API endpoints work correctly.

**Prerequisites:**
1. Start the FastAPI backend server
2. MongoDB should be accessible (or you can use a local MongoDB)

**Run integration tests:**

```bash
# Terminal 1: Start the API server
cd apps/api
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Run integration tests
cd apps/api
source venv/bin/activate
pip install requests  # If not already installed
python scripts/integration_test.py
```

The integration tests will:
- ✓ Check API health
- ✓ Test root endpoint
- ✓ Test CV upload (validation)
- ✓ Test profile save
- ✓ Test profile retrieval
- ✓ Test profile update

### Frontend Build Test

Verify the Next.js frontend builds correctly:

```bash
cd apps/web
npm run build
```

Expected output: Build should complete successfully without errors.

## Manual End-to-End Testing

### 1. Start the Backend

```bash
cd apps/api
source venv/bin/activate

# Set up environment (optional - for MongoDB Atlas)
cp .env.example .env
# Edit .env with your MongoDB connection string

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs (Swagger UI)

### 2. Start the Frontend

```bash
cd apps/web
npm run dev
```

The web app will be available at: http://localhost:3000

### 3. Test the Flow

1. **Visit the home page**: http://localhost:3000
   - Should see the Jobly landing page with features and links

2. **Navigate to Profile page**: http://localhost:3000/profile or click "Manage Profile"
   - Should see the CV upload interface

3. **Upload a CV** (PDF or DOCX):
   - Click "Select PDF or DOCX file"
   - Choose a CV file
   - Click "Upload & Parse CV"
   - Should see:
     - Success message
     - Extracted text preview
     - Editable profile form with auto-populated data

4. **Edit Profile**:
   - Update name, email, summary
   - Add/edit skills groups
   - Add/edit experience roles and bullets
   - Add/remove links

5. **Set Preferences** (switch to "Job Preferences" tab):
   - Toggle "Open to Europe" and "Remote OK"
   - Select preferred countries
   - Enter cities (comma-separated)
   - Select languages
   - Add skill tags and role tags

6. **Save Profile**:
   - Click "Save Profile" or "Save Preferences"
   - Should see success message with profile ID

7. **Verify Profile is Saved**:
   - Option 1: Refresh the page and use the API to get the profile
   - Option 2: Check MongoDB for the saved profile
   - Option 3: Use the API docs at http://localhost:8000/docs to test GET /profile

### 4. Test API Directly (Using Swagger UI)

Visit http://localhost:8000/docs to test the API endpoints interactively:

1. **POST /profile/upload-cv**:
   - Click "Try it out"
   - Upload a PDF or DOCX file
   - Execute
   - Should return extracted text and draft profile

2. **POST /profile/save**:
   - Click "Try it out"
   - Paste a profile JSON (use example_seed_profile.json as template)
   - Execute
   - Should return profile_id

3. **GET /profile**:
   - Click "Try it out"
   - Optionally enter an email
   - Execute
   - Should return saved profile

4. **PATCH /profile**:
   - Click "Try it out"
   - Enter email and update fields
   - Execute
   - Should return updated profile_id

## Testing Without MongoDB

If you don't have MongoDB Atlas set up, the API will attempt to connect and may show errors. However, you can still test:

1. CV extraction and parsing (doesn't require DB)
2. Schema validation
3. API structure and responses (will fail on DB operations)

For full testing, set up a free MongoDB Atlas cluster:
1. Go to https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get connection string
4. Update `apps/api/.env` with your connection string

## Common Issues

### Issue: "email-validator is not installed"
**Solution:** 
```bash
cd apps/api
source venv/bin/activate
pip install email-validator
```

### Issue: "Failed to fetch fonts from Google Fonts"
**Solution:** This has been fixed in the latest code. The layout.tsx no longer uses Google Fonts.

### Issue: "Cannot connect to MongoDB"
**Solution:** 
- Ensure MongoDB is running (local or Atlas)
- Check your connection string in `.env`
- For testing without MongoDB, some endpoints will fail but CV parsing will still work

### Issue: "Port already in use"
**Solution:**
```bash
# Find process using port 8000
ps aux | grep uvicorn
# Kill the process
kill <PID>
```

## Success Criteria

All of the following should work:

- ✅ Upload PDF/DOCX CV and extract text
- ✅ Generate valid UserProfile draft from CV
- ✅ Edit profile fields (name, email, skills, experience)
- ✅ Set job preferences (location, skills, roles)
- ✅ Save profile to MongoDB
- ✅ Retrieve saved profile
- ✅ Update profile fields
- ✅ All unit tests pass
- ✅ Integration tests pass (with MongoDB)
- ✅ Frontend builds successfully
- ✅ UI is responsive and functional
