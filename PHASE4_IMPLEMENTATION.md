# Phase 4: Tailored CV Generation & Application Packets - Implementation Guide

## Overview

Phase 4 implements automated generation of tailored CVs and complete application packets for each job. The system creates job-specific materials including LaTeX CVs (with optional PDF compilation), cover letters, recruiter messages, and common application answers.

## Key Features

### 1. Tailored CV Generation
- **LaTeX Templates**: Professional CV templates using moderncv class
- **Job-Specific Tailoring**: Customized summary, prioritized skills, and optimized content
- **Deterministic Layout**: Budget-based control ensures CVs fit in 2 pages
- **PDF Compilation**: Optional latexmk compilation when available
- **Truthful Output**: No fabricated claims or invented experience

### 2. Application Packet Components
Each packet includes:
- **CV (.tex)**: Always generated, compatible with Overleaf
- **CV (.pdf)**: Generated when LaTeX tools are available
- **Cover Letter**: Optional, customizable
- **Recruiter Message**: Brief outreach message for direct contact
- **Common Answers**: Prepared responses for typical application questions

### 3. Integrity & Transparency
- **Gap Analysis**: Identifies missing skills/requirements
- **Integrity Notes**: Warns about significant gaps
- **Evidence-Based**: Bullet suggestions cite evidence where available
- **No Fabrication**: System never invents experience or metrics

## Architecture

### Backend (FastAPI)

#### Schemas (`app/schemas/packet.py`)
```python
- BulletSwap: Suggested bullet improvements
- TailoringPlan: Structured tailoring strategy
- PacketFile: File metadata with integrity hash
- Packet: Complete packet with all materials
- GeneratePacketRequest: API request model
```

#### Services

**Tailoring Service** (`app/services/tailoring.py`)
- `generate_tailoring_plan()`: Creates structured plan from job + profile
- `render_latex_cv()`: Renders LaTeX CV from plan
- `compile_latex()`: Optional PDF compilation
- `generate_cover_letter()`: Creates cover letter
- `generate_recruiter_message()`: Creates outreach message
- `generate_common_answers()`: Creates application Q&A

**Storage Service** (`app/services/packet_storage.py`)
- File system storage with configurable `PACKETS_DIR`
- Path sanitization for security
- MongoDB metadata storage
- File integrity via SHA256 hashes

#### Templates (`app/templates/latex/`)
- `base.tex.j2`: Main CV template using Jinja2 with custom delimiters
- Uses moderncv LaTeX class for professional formatting
- Configurable sections and budgets

#### API Endpoints (`app/routers/packets.py`)
```
POST /packets/generate
  - Generates complete packet for a job
  - Request: job_id, include_cover_letter, user_emphasis
  - Returns: Packet with all files

GET /packets/{packet_id}
  - Retrieves packet metadata

GET /packets
  - Lists packets with filtering

GET /packets/{packet_id}/download/{file_type}
  - Downloads specific file (tex, pdf, cover_letter, etc.)
```

### Frontend (Next.js)

#### Types (`types/packet.ts`)
TypeScript interfaces matching backend schemas

#### Pages
**Packet Detail** (`app/packets/[id]/page.tsx`)
- Displays tailored summary
- Shows priority skills and gaps
- Lists integrity notes
- Provides download links for all files
- Shows bullet improvement suggestions

**Matches Page Updates** (`app/matches/page.tsx`)
- "Generate Packet" button in table rows
- "Generate Packet" button in detail modal
- Automatic navigation to packet page after generation

## Tailoring Algorithm

The tailoring service uses rule-based, deterministic methods:

### 1. Skill Extraction
- Regex-based extraction of technical skills from job description
- Matches common languages, frameworks, databases, cloud, DevOps tools

### 2. Summary Rewriting
- Prepends interest in specific role and company
- Keeps existing summary content
- Limits to 3 sentences

### 3. Skill Prioritization
- Matches user skills against job requirements
- Places matching skills first
- Preserves non-matching skills after

### 4. Bullet Suggestions
- Identifies bullets that mention required skills
- Suggests emphasizing those skills
- Does NOT fabricate new content
- Provides evidence references when available

### 5. Gap Identification
- Compares job requirements to user profile
- Checks explicit skills and experience bullets
- Lists missing requirements

### 6. Layout Control
Deterministic budgeting ensures 2-page limit:
- `max_roles`: Maximum experience entries (default: 4)
- `bullets_per_role`: Maximum bullets per role (default: 4)
- `max_projects`: Maximum project entries (default: 3)

## LaTeX Compilation

### When Available
If `latexmk` is installed:
1. Writes .tex file to packet directory
2. Runs `latexmk -pdf -interaction=nonstopmode`
3. Saves resulting PDF to packet
4. Both .tex and .pdf available for download

### Fallback
If `latexmk` is not available:
1. Only .tex file is generated
2. User can compile locally or on Overleaf
3. API response indicates compilation status

### Installation
See README for platform-specific installation instructions.

## Storage Strategy

### File System
- Files stored in `PACKETS_DIR` (default: `/tmp/jobly_packets`)
- Each packet has subdirectory: `PACKETS_DIR/{packet_id}/`
- Files: `cv.tex`, `cv.pdf`, `cover_letter.txt`, etc.

### MongoDB
- Collection: `packets`
- Stores packet metadata and file references
- File paths are relative to `PACKETS_DIR`
- SHA256 hashes for integrity verification

### Security
- Path sanitization prevents traversal attacks
- Only alphanumeric, dash, underscore, dot allowed in filenames
- Packet IDs are MongoDB ObjectIDs

## Testing

### Unit Tests (`tests/test_packets.py`)
- Schema validation
- Skill extraction
- Summary rewriting
- Skill prioritization
- Gap identification
- LaTeX rendering
- Message generation

### Integration Tests
Manual testing recommended:
1. Generate packet via UI
2. Verify files are created
3. Download each file type
4. Check LaTeX compilation (if available)
5. Verify content accuracy

## Configuration

### Environment Variables
```bash
# Required
MONGODB_URI=mongodb+srv://...
MONGODB_DB_NAME=jobly

# Optional
PACKETS_DIR=/tmp/jobly_packets  # File storage location
```

### Template Customization
Edit `apps/api/app/templates/latex/base.tex.j2`:
- Modify LaTeX structure
- Adjust spacing and formatting
- Change section order
- Customize appearance

## Future Enhancements

### Phase 5 (Planned)
- Interview Q&A generation
- Company research integration
- Practice questions

### Phase 6 (Planned)
- Playwright-based application prefilling
- Auto-fill web forms
- Track application status

## Best Practices

### For Users
1. **Review Before Sending**: Always review generated materials
2. **Customize**: Edit the .tex file or regenerate with emphasis
3. **Verify Truthfulness**: Check all claims are accurate
4. **Update Profile**: Keep profile current for best results

### For Developers
1. **Never Fabricate**: Do not invent experience or metrics
2. **Cite Evidence**: Reference source when suggesting changes
3. **Preserve Intent**: Maintain user's original voice and style
4. **Test Thoroughly**: Verify output quality and accuracy

## Troubleshooting

### LaTeX Compilation Fails
- Check if latexmk is installed: `latexmk -version`
- Verify TeX distribution is complete
- Check log files in packet directory
- Use .tex file as fallback

### Files Not Generating
- Check PACKETS_DIR permissions
- Verify MongoDB connection
- Check API logs for errors
- Ensure sufficient disk space

### Template Errors
- Verify Jinja2 syntax in templates
- Check for LaTeX special character escaping
- Test with minimal profile data
- Review template rendering logs

## API Examples

### Generate Packet
```bash
curl -X POST http://localhost:8000/packets/generate \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "507f1f77bcf86cd799439011",
    "include_cover_letter": true,
    "user_emphasis": ["emphasize AWS experience"]
  }'
```

### List Packets
```bash
curl http://localhost:8000/packets?job_id=507f1f77bcf86cd799439011
```

### Download File
```bash
curl http://localhost:8000/packets/{packet_id}/download/pdf \
  --output cv.pdf
```

## Conclusion

Phase 4 provides a complete, automated solution for generating tailored application materials. The system prioritizes truthfulness, transparency, and user control while automating the tedious parts of job applications.
