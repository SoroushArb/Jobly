# Jobly Web - Frontend

Next.js frontend for the AI Job Hunter Agent with full-featured UI for all six phases.

## Overview

The Jobly web application provides a beautiful, responsive interface for:
- **Profile Management**: Upload CV, edit profile, set job preferences
- **Job Discovery**: Browse jobs with advanced filters
- **AI Matching**: View ranked job matches with explanations
- **Packet Generation**: Generate tailored CVs and application materials
- **Interview Prep**: AI-powered interview preparation materials
- **Application Tracking**: Manage your application pipeline

## Tech Stack

- **Next.js 16**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **React Hooks**: State management and effects

## Prerequisites

- Node.js 18+
- Backend API running at http://localhost:8000 (or configured URL)

## Setup

### 1. Install Dependencies

```bash
cd apps/web
npm install
```

### 2. Configure Environment

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, set this to your deployed backend URL.

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at http://localhost:3000

## Environment Variables

### `NEXT_PUBLIC_API_URL`
- **Description**: Backend API base URL
- **Default**: `http://localhost:8000`
- **Required**: No (falls back to default)
- **Production**: Set to your deployed API URL

Example:
```bash
# Local development
NEXT_PUBLIC_API_URL=http://localhost:8000

# Production
NEXT_PUBLIC_API_URL=https://api.jobly.example.com
```

## Application Routes

### Core Pages

- **`/`**: Home page with overview and navigation
- **`/profile`**: Profile management and CV upload
- **`/jobs`**: Job browsing with filters and search
- **`/matches`**: AI-powered job matches with rankings
- **`/packets/[id]`**: Application packet details
- **`/interview/[packet_id]`**: Interview preparation materials
- **`/applications`**: Application tracking dashboard

### API Routes

The frontend communicates with the backend via REST API:
- Profile operations: `/profile/*`
- Job operations: `/jobs/*`
- Match operations: `/matches/*`
- Packet operations: `/packets/*`
- Interview operations: `/interview/*`
- Application operations: `/applications/*`

## Key Workflows

### Phase 1: Profile Setup

1. Navigate to `/profile`
2. Upload CV (PDF or DOCX)
3. Review auto-extracted data
4. Edit profile fields as needed
5. Set job preferences (location, remote, skills, roles)
6. Save profile

### Phase 2: Job Discovery

1. Navigate to `/jobs`
2. Click "Trigger Job Ingestion" to fetch latest jobs
3. Browse job listings in table view
4. Filter by:
   - Remote type (remote, hybrid, onsite)
   - Country and city
   - Keywords in title/description
5. Click "View" to see full job details in modal
6. Click "Apply →" to visit original job posting

### Phase 3: Job Matching

1. Navigate to `/matches`
2. Click "Recompute Matches" to run AI matching
3. View ranked job matches sorted by score
4. Filter by:
   - Minimum score
   - Remote type
   - Country and city
   - Skill tags
5. Click "View Details" to see:
   - Match score breakdown
   - Top reasons for match
   - Identified gaps
   - Recommendations
6. Click "Generate Packet" for selected job

### Phase 4: Application Packets

1. Redirected to `/packets/[id]` after generation
2. View tailored CV details:
   - Professional summary rewritten for job
   - Prioritized skills
   - Identified gaps and suggestions
3. Download files:
   - CV LaTeX (.tex) - always available
   - CV PDF (.pdf) - if LaTeX installed
   - Cover Letter
   - Recruiter Message
   - Common Application Answers
4. Use materials for application

### Phase 5: Interview Preparation

1. From packet page, click "Prepare Interview"
2. View comprehensive prep materials:
   - 30/60/90 day plan
   - STAR stories grounded in experience
   - Questions to ask interviewer
   - Study checklist for gaps
   - Technical Q&A (searchable, filterable)
3. Search and filter technical questions by:
   - Keywords
   - Difficulty (easy/medium/hard)
   - Topic
4. Export complete prep pack as Markdown
5. Study offline

### Phase 6: Application Tracking

1. From packet page, click "Create Application"
2. Application created in "prepared" status
3. Click "Open & Prefill" to generate token
4. Copy command and run local agent (see [local-agent docs](../local-agent/README.md))
5. After prefill, application status updates to "prefilled"
6. Navigate to `/applications` to track all applications
7. Filter by status (prepared, prefilled, applied, interviewed, offered, etc.)
8. Update status manually as you progress

## Project Structure

```
apps/web/
├── app/                      # Next.js App Router pages
│   ├── page.tsx              # Home page
│   ├── profile/page.tsx      # Profile management
│   ├── jobs/page.tsx         # Job browsing
│   ├── matches/page.tsx      # AI job matching
│   ├── packets/[id]/page.tsx # Packet details
│   ├── interview/[packet_id]/page.tsx  # Interview prep
│   └── applications/page.tsx # Application tracking
├── components/               # React components
│   ├── CVUpload.tsx          # CV upload component
│   ├── JobList.tsx           # Job listing table
│   ├── MatchesList.tsx       # Match display
│   └── ...                   # Other UI components
├── lib/
│   └── api.ts                # API client utilities
├── types/
│   └── index.ts              # TypeScript type definitions
├── public/                   # Static assets
├── package.json              # Dependencies
└── README.md                 # This file
```

## Development

### Build for Production

```bash
npm run build
```

### Run Production Build

```bash
npm start
```

### Linting

```bash
npm run lint
```

## API Integration

The frontend uses `fetch` to communicate with the FastAPI backend. All API calls go through the configured `NEXT_PUBLIC_API_URL`.

Example API client (`lib/api.ts`):
```typescript
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getProfile() {
  const response = await fetch(`${apiUrl}/profile`);
  return response.json();
}
```

## Styling

### Tailwind CSS

The app uses Tailwind CSS for styling. Key utilities:
- Responsive design: `sm:`, `md:`, `lg:` prefixes
- Dark mode: Not currently implemented
- Custom colors: Defined in `tailwind.config.js`

### Component Patterns

- **Layout**: Consistent page layout with navigation
- **Cards**: Used for job listings, match details
- **Modals**: Job details, match explanations
- **Forms**: Profile editing, filters
- **Tables**: Job and application listings

## Common Development Tasks

### Adding a New Page

1. Create file in `app/newpage/page.tsx`
2. Add navigation link in layout
3. Create necessary components in `components/`
4. Add API calls in `lib/api.ts`

### Adding a New API Endpoint

1. Update `lib/api.ts` with new function
2. Use in component with React hooks
3. Handle loading and error states

### Updating Types

1. Update `types/index.ts`
2. Ensure consistency with backend schemas
3. Run `npm run build` to check for type errors

## Troubleshooting

### Cannot connect to backend

**Error**: `Failed to fetch` or `Network error`

**Solution**:
1. Ensure backend is running at configured URL
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS is configured on backend
4. Check browser console for detailed errors

### Build errors

**Error**: TypeScript errors during `npm run build`

**Solution**:
1. Run `npm run lint` to identify issues
2. Check for type mismatches with backend API
3. Update types in `types/index.ts`

### Styles not applying

**Error**: Tailwind classes not working

**Solution**:
1. Restart dev server after config changes
2. Check class names for typos
3. Verify `tailwind.config.js` is correct

## Production Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variable: `NEXT_PUBLIC_API_URL=https://your-api.com`
4. Deploy

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t jobly-web .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=https://api.example.com jobly-web
```

### Environment Variables in Production

Always set:
- `NEXT_PUBLIC_API_URL`: Your production backend URL
- `NODE_ENV=production`: Automatically set by most platforms

## Further Documentation

- [Root README](../../README.md): Full project overview
- [API README](../api/README.md): Backend API documentation
- [Local Agent README](../local-agent/README.md): Automation agent setup
- [Quickstart Guide](../../docs/QUICKSTART.md): End-to-end setup
- [Environment Variables](../../docs/ENVIRONMENT.md): Complete env var reference
- [Troubleshooting](../../docs/TROUBLESHOOTING.md): Common issues and solutions

## License

MIT
