# Deploying Jobly to Koyeb

This guide walks you through deploying Jobly to Koyeb, a serverless platform that supports containerized applications.

## Architecture Overview

Jobly consists of three services:
1. **API**: FastAPI backend (handles HTTP requests, SSE streams)
2. **Worker**: Background job processor (handles async tasks)
3. **Web**: Next.js frontend (user interface)

All three services will be deployed to Koyeb, with MongoDB Atlas as the database and GridFS for file storage.

## Prerequisites

1. **Koyeb Account**: Sign up at [https://www.koyeb.com](https://www.koyeb.com)
2. **MongoDB Atlas**: Create a free cluster at [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
3. **OpenAI API Key**: Get from [https://platform.openai.com](https://platform.openai.com)
4. **GitHub Repository**: Your Jobly code should be in a GitHub repository

## Step 1: Set Up MongoDB Atlas

1. Create a MongoDB Atlas cluster (Free M0 tier works for testing)
2. Create a database user with read/write permissions
3. Whitelist `0.0.0.0/0` in Network Access (to allow Koyeb access)
4. Get your connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

## Step 2: Prepare Environment Variables

You'll need these environment variables for your services:

### API Service Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `MONGODB_URI` | ✅ Yes | MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster.mongodb.net/jobly?retryWrites=true&w=majority` |
| `MONGODB_DB_NAME` | ✅ Yes | Database name | `jobly` |
| `CORS_ORIGINS` | ✅ Yes | Allowed origins for CORS | `https://your-web-app.koyeb.app` |
| `PORT` | ✅ Yes | Port to bind (Koyeb provides this) | `8000` |
| `USE_GRIDFS` | ✅ Yes | Use GridFS for file storage | `true` |
| `OPENAI_API_KEY` | ✅ Yes | OpenAI API key for LLM and embeddings | `sk-...` |
| `LLM_PROVIDER` | No | LLM provider | `openai` (default) |
| `LLM_MODEL` | No | LLM model | `gpt-4o-mini` (default) |
| `EMBEDDING_PROVIDER` | No | Embedding provider | `openai` (default) |
| `OPENAI_EMBEDDING_MODEL` | No | Embedding model | `text-embedding-3-small` (default) |

### Worker Service Environment Variables

Same as API service (the worker shares the same codebase and configuration).

### Web Service Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | ✅ Yes | API base URL (build-time) | `https://your-api-app.koyeb.app` |
| `PORT` | ✅ Yes | Port to bind | `3000` |

**Important**: `NEXT_PUBLIC_API_URL` must be set at **build time** for Next.js. You'll need to rebuild the web service if you change the API URL.

## Step 3: Deploy API Service

1. Go to Koyeb Dashboard
2. Click **Create Service**
3. Choose **GitHub** as deployment method
4. Select your repository
5. Configure the service:
   - **Service Type**: Web Service
   - **Name**: `jobly-api`
   - **Region**: Choose closest to your users
   - **Build**:
     - Builder: Docker
     - Dockerfile path: `apps/api/Dockerfile`
     - **Note**: Koyeb uses the repository root as the build context by default. The Dockerfiles are already configured to work with repo-root context, so you don't need to specify a custom build context.
   - **Port**: `8000`
   - **Health Check**: `/healthz` (HTTP GET)
   - **Environment Variables**: Add all API env vars from table above
   - **Scaling**: Start with 1 instance (nano or micro)
6. Click **Deploy**

Wait for deployment to complete. Note the URL (e.g., `https://jobly-api-your-org.koyeb.app`)

## Step 4: Deploy Worker Service

1. Click **Create Service** again
2. Choose **GitHub** as deployment method
3. Select your repository
4. Configure the service:
   - **Service Type**: Worker
   - **Name**: `jobly-worker`
   - **Region**: Same as API for lower latency
   - **Build**:
     - Builder: Docker
     - Dockerfile path: `apps/worker/Dockerfile`
     - **Note**: Koyeb uses the repository root as the build context by default. The Dockerfiles are already configured to work with repo-root context, so you don't need to specify a custom build context.
   - **Environment Variables**: Add all Worker env vars (same as API)
   - **Scaling**: Start with 1 instance (nano or micro)
5. Click **Deploy**

**Note**: Worker is a background service with no public endpoint.

## Step 5: Deploy Web Service

1. Click **Create Service** again
2. Choose **GitHub** as deployment method
3. Select your repository
4. Configure the service:
   - **Service Type**: Web Service
   - **Name**: `jobly-web`
   - **Region**: Choose closest to your users
   - **Build**:
     - Builder: Docker
     - Dockerfile path: `apps/web/Dockerfile`
     - **Note**: Koyeb uses the repository root as the build context by default. The Dockerfiles are already configured to work with repo-root context, so you don't need to specify a custom build context.
     - **Build Args**:
       - `NEXT_PUBLIC_API_URL=https://jobly-api-your-org.koyeb.app`
   - **Port**: `3000`
   - **Health Check**: `/` (HTTP GET)
   - **Environment Variables**:
     - `NEXT_PUBLIC_API_URL=https://jobly-api-your-org.koyeb.app`
     - `PORT=3000`
   - **Scaling**: Start with 1 instance (nano or micro)
5. Click **Deploy**

Wait for deployment. Note the URL (e.g., `https://jobly-web-your-org.koyeb.app`)

## Step 6: Update CORS Configuration

1. Go back to your API service settings
2. Update the `CORS_ORIGINS` environment variable to include your web app URL:
   ```
   https://jobly-web-your-org.koyeb.app
   ```
3. Redeploy the API service

## Step 7: Verify Deployment

1. Visit your web app URL
2. Check that the homepage loads
3. Test API connectivity:
   - Visit `https://jobly-api-your-org.koyeb.app/healthz`
   - Should return `{"status":"healthy"}`
   - Visit `https://jobly-api-your-org.koyeb.app/readyz`
   - Should return `{"status":"ready","database":"connected"}`

## Step 8: Test Background Jobs

1. Upload a CV through the web interface
2. Trigger job ingestion (Jobs page)
3. Monitor progress via the real-time updates (SSE)
4. Check worker logs in Koyeb dashboard to see job processing

## Scaling Considerations

### API Service
- **Recommended**: 2+ instances for high availability
- **Auto-scaling**: Enable based on CPU or memory usage
- **Instance Size**: Start with micro, scale to small/medium under load

### Worker Service
- **Recommended**: 1-2 instances (depends on job volume)
- **Auto-scaling**: Consider scaling based on job queue length
- **Instance Size**: Small or medium (LaTeX compilation can be resource-intensive)

### Web Service
- **Recommended**: 2+ instances for high availability
- **Auto-scaling**: Enable based on request rate
- **Instance Size**: Nano or micro (Next.js is lightweight)

## Monitoring

### Health Checks
- API: `/healthz` (liveness), `/readyz` (readiness)
- Web: `/` (homepage)

### Logs
Check Koyeb logs for each service:
- API logs: HTTP requests, database operations
- Worker logs: Job processing, progress updates
- Web logs: Next.js server logs

### Database Monitoring
Use MongoDB Atlas dashboard to monitor:
- Connection count
- Query performance
- Storage usage (GridFS files)

## Troubleshooting

### API Returns 503 on /readyz
- Check MongoDB Atlas connection string
- Verify network access whitelist includes `0.0.0.0/0`
- Check MongoDB Atlas cluster is running

### Worker Not Processing Jobs
- Check worker logs for errors
- Verify worker has same environment variables as API
- Check MongoDB connection

### CORS Errors in Browser
- Verify `CORS_ORIGINS` includes web app URL
- Redeploy API after changing CORS settings
- Check browser console for exact error

### Web App Can't Connect to API
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Rebuild web service if API URL changed
- Check API health endpoints are accessible

### Jobs Stuck in Queued Status
- Check worker logs
- Verify worker is running
- Check database indexes were created (API startup logs)

## Cost Optimization

### Koyeb Free Tier
- 2 GB RAM total across all services
- Suitable for testing and small deployments
- Consider:
  - API: 512 MB
  - Worker: 1 GB (for LaTeX)
  - Web: 512 MB

### MongoDB Atlas Free Tier
- M0 cluster: 512 MB storage
- Good for testing and small projects
- GridFS files count toward storage limit

### Production Recommendations
- **Koyeb**: Upgrade to paid plan for:
  - More resources
  - Auto-scaling
  - Custom domains
  - Better SLA
- **MongoDB Atlas**: Upgrade to M10+ for:
  - More storage
  - Better performance
  - Automated backups
  - Point-in-time recovery

## Security Best Practices

1. **Secrets Management**
   - Never commit secrets to Git
   - Use Koyeb's encrypted environment variables
   - Rotate API keys regularly

2. **Database Security**
   - Use strong MongoDB passwords
   - Enable MongoDB Atlas IP whitelist (restrict to Koyeb IPs if possible)
   - Enable MongoDB authentication

3. **Network Security**
   - Use HTTPS for all services (Koyeb provides this automatically)
   - Restrict CORS origins to only your web app
   - Consider adding rate limiting

4. **Application Security**
   - Keep dependencies updated
   - Monitor security advisories
   - Enable Koyeb security scanning

## Local Development vs. Production

### Local Development
- Use filesystem storage (`USE_GRIDFS=false`)
- Use local MongoDB or MongoDB Atlas
- Run services with `docker-compose up`

### Production (Koyeb)
- Use GridFS storage (`USE_GRIDFS=true`)
- Use MongoDB Atlas
- Services auto-scale and auto-heal

## Support and Resources

- **Koyeb Docs**: [https://www.koyeb.com/docs](https://www.koyeb.com/docs)
- **MongoDB Atlas Docs**: [https://docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)
- **Jobly GitHub**: Report issues and feature requests
- **Koyeb Community**: [https://community.koyeb.com](https://community.koyeb.com)

## Next Steps

After successful deployment:
1. Set up custom domain (optional)
2. Configure monitoring and alerts
3. Set up automated backups
4. Plan scaling strategy based on usage
5. Consider CDN for static assets
6. Implement additional security measures

---

**Note**: The local Playwright agent runs on your machine and is NOT deployed to Koyeb. It connects to the deployed API via short-lived tokens.
