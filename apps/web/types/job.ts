// Job posting types matching backend schemas

export interface JobPosting {
  // Core job information
  company: string;
  title: string;
  url: string;
  location?: string;
  country?: string;
  city?: string;
  remote_type: "onsite" | "hybrid" | "remote" | "unknown";
  
  // Job description
  description_raw?: string;
  description_clean?: string;
  
  // Optional fields
  posted_date?: string;
  employment_type?: string;
  
  // Source metadata
  source_name: string;
  source_type: "company" | "rss" | "api";
  source_compliance_note?: string;
  fetched_at: string;
  
  // Deduplication
  dedupe_hash: string;
  
  // Persistence tracking
  first_seen: string;
  last_seen: string;
}

export interface JobPostingInDB extends JobPosting {
  _id?: string;
  id?: string;
}

export interface JobListResponse {
  jobs: JobPostingInDB[];
  total: number;
  page: number;
  per_page: number;
  message: string;
}

export interface JobPostingResponse {
  job: JobPostingInDB;
  message: string;
}

export interface IngestResponse {
  jobs_fetched: number;
  jobs_new: number;
  jobs_updated: number;
  sources_processed: string[];
  message: string;
}

export interface JobFilters {
  remote_type?: string;
  remote?: boolean;
  country?: string;
  city?: string;
  keyword?: string;
  page?: number;
  per_page?: number;
}
