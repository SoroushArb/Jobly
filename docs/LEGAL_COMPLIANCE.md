# Legal & Compliance Guide

Guidelines for responsible and legal job data collection in Jobly.

## Overview

Jobly is designed to aggregate job postings from **publicly available, legal sources only**. This document outlines the compliance framework and best practices for adding job sources.

## Core Principles

1. **Public Data Only**: Only collect data that is publicly accessible without authentication
2. **Respect robots.txt**: Honor website crawling policies
3. **Rate Limiting**: Be polite and avoid overwhelming servers
4. **Terms of Service**: Comply with each source's terms of service
5. **Attribution**: Properly attribute job postings to their source
6. **No Scraping**: Prefer official APIs and RSS feeds over web scraping

## Recommended Job Sources

### ✅ RSS/Atom Feeds (Preferred)

RSS feeds are explicitly designed for syndication and are the safest option:

- **Stack Overflow Jobs**: `https://stackoverflow.com/jobs/feed`
- **RemoteOK**: `https://remoteok.com/remote-dev-jobs.rss`
- **We Work Remotely**: Various RSS feeds by category
- **GitHub Jobs**: RSS feeds when available
- **AngelList**: Public RSS feeds

**Why RSS is safe:**
- Explicitly published for consumption
- No authentication required
- Respects rate limits by design
- Clear terms of use

### ✅ Official APIs (Best Option)

If available, use official job board APIs:

- **Adzuna API**: Free tier available
- **The Muse API**: Public API with rate limits
- **GitHub Jobs API**: Official REST API (if still available)
- **Glassdoor API**: Partner program

**Requirements:**
- Register for API key
- Read API terms of service
- Respect rate limits
- Provide proper attribution

### ⚠️ Company Career Pages (Use with Caution)

Public career pages are generally acceptable but require care:

**Check Before Scraping:**
1. Review `robots.txt` at `https://example.com/robots.txt`
2. Check for "Disallow: /careers" or similar directives
3. Read the website's terms of service
4. Look for explicit scraping policies

**Best Practices:**
- Use respectful rate limits (60-120 seconds between requests)
- Set a descriptive User-Agent header
- Only collect public information
- Don't use authentication or bypass access controls
- Keep records of compliance checks

**Example Configuration:**
```yaml
- name: "Example Company Careers"
  type: "company"
  enabled: true
  url: "https://example.com/careers"
  compliance_note: "Public careers page - robots.txt allows, checked 2024-01-15"
  rate_limit_seconds: 120
```

### ❌ Prohibited Sources

**Do NOT use:**
- Sites that require authentication or login
- Sites with "Disallow" in robots.txt for career pages
- Sites with terms explicitly prohibiting scraping
- LinkedIn (without official API partnership)
- Indeed (without official API)
- Premium/paid job boards without permission
- Sites using aggressive anti-bot measures (respect their wishes)

## Configuration File: `job_sources_config.yaml`

Location: `apps/api/job_sources_config.yaml`

### Required Fields

Every source must include:

```yaml
sources:
  - name: "Source Name"                    # Human-readable name
    type: "rss|company"                    # Source type
    enabled: true|false                    # Enable/disable source
    url: "https://..."                     # Source URL
    compliance_note: "Compliance reason"   # Why this source is legal
    rate_limit_seconds: 60                 # Minimum seconds between requests
```

### Compliance Notes

Every source **must** have a compliance note explaining why it's legal to use:

**Good Examples:**
- "Public RSS feed - Terms of Service compliant"
- "Public API - Registered API key, following rate limits"
- "Public careers page - robots.txt allows, no auth required"
- "Official data sharing agreement in place"

**Bad Examples:**
- "Public website" (too vague)
- "Found on Google" (not a legal justification)
- "" (empty - not acceptable)

### Global Settings

```yaml
settings:
  default_rate_limit_seconds: 60              # Default rate limit
  respect_robots_txt: true                     # Always keep true
  user_agent: "Jobly/1.0 (Job Aggregator...)" # Descriptive User-Agent
  max_retries: 3                               # Max retry attempts
  timeout_seconds: 30                          # Request timeout
```

## Adding New Sources

### Checklist

Before adding a new source:

- [ ] Verify data is publicly available (no login required)
- [ ] Check `robots.txt` if applicable
- [ ] Read the terms of service
- [ ] Verify no explicit anti-scraping clauses
- [ ] Determine appropriate rate limit
- [ ] Write clear compliance note
- [ ] Test source locally first
- [ ] Document any special requirements

### Process

1. **Research**: Investigate the source's policies
2. **Test**: Try fetching data manually to verify accessibility
3. **Configure**: Add to `job_sources_config.yaml` with compliance note
4. **Enable**: Set `enabled: true` only after testing
5. **Monitor**: Check logs for errors or blocking

### Example: Adding an RSS Feed

```yaml
- name: "TechCareers RSS"
  type: "rss"
  enabled: true
  url: "https://techcareers.example/feed.rss"
  compliance_note: "Public RSS feed - Terms allow syndication (checked 2024-01-15)"
  rate_limit_seconds: 60
```

### Example: Adding a Company Page

```yaml
- name: "Acme Corp Careers"
  type: "company"
  enabled: true
  url: "https://acme.example/careers"
  compliance_note: "Public careers page - robots.txt allows /careers, no auth (checked 2024-01-15)"
  rate_limit_seconds: 120
  parser_config:
    job_list_selector: ".job-card"
    title_selector: ".job-title"
    location_selector: ".job-location"
    link_selector: "a.job-link"
```

## Rate Limiting

### Recommended Rates

- **RSS Feeds**: 60 seconds minimum
- **APIs**: Follow provider's rate limits (often 1-10 req/sec)
- **Company Pages**: 120 seconds minimum
- **Unknown**: 120 seconds (be conservative)

### Implementation

Rate limits are enforced at the source level in `apps/api/app/services/sources/rss_source.py` and `company_source.py`.

## Robots.txt Compliance

### What is robots.txt?

A file at `https://example.com/robots.txt` that specifies crawling rules.

### How to Check

```bash
curl https://example.com/robots.txt
```

Look for:
```
User-agent: *
Disallow: /careers  # ❌ Don't scrape
```

vs.

```
User-agent: *
Allow: /careers     # ✅ OK to scrape
# or no mention of /careers (also OK)
```

### Jobly Implementation

Set `respect_robots_txt: true` in global settings (default).

## User-Agent String

Always use a descriptive User-Agent:

```
Jobly/1.0 (Job Aggregator; +https://github.com/SoroushArb/Jobly)
```

This identifies your bot and provides contact information.

## Data Retention & Privacy

### What We Store

- Job title, company, description
- Location, employment type
- Application URL
- Source metadata (name, type, compliance note)

### What We DON'T Store

- Personal candidate information from other users
- Authentication credentials
- Private/internal job postings
- Salary data (unless publicly posted)

### User Privacy

- Only store user's own profile data
- Don't share profiles with third parties
- Users can delete their data anytime

## Legal Disclaimer

**This is not legal advice.** Jobly is provided as-is for personal use. Users are responsible for:

- Ensuring their use complies with local laws
- Respecting terms of service of job sources
- Using scraped data responsibly and ethically
- Not using Jobly for commercial data resale

If you're uncertain about a source's legality, **don't add it**.

## Reporting Issues

If you discover:
- A source that shouldn't be used
- A compliance violation
- A robots.txt conflict
- Terms of service that prohibit our use

Please:
1. Disable the source immediately in `job_sources_config.yaml`
2. Open a GitHub issue with details
3. Remove the source from future use

## Resources

- **robots.txt spec**: https://www.robotstxt.org/
- **RSS Best Practices**: https://www.rssboard.org/
- **Web Scraping Legality**: Consult with a lawyer in your jurisdiction
- **GDPR Compliance** (EU): https://gdpr.eu/

## Summary

✅ **Do:**
- Use public RSS feeds
- Use official APIs with proper registration
- Respect robots.txt and rate limits
- Provide clear compliance notes
- Be transparent with User-Agent

❌ **Don't:**
- Scrape sites that disallow it
- Bypass authentication or paywalls
- Ignore rate limits or terms of service
- Use data for commercial resale
- Collect private or personal information

When in doubt, **err on the side of caution** and choose a different source.
