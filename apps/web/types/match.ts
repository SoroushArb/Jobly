export interface ScoreBreakdown {
  semantic: number;
  skill_overlap: number;
  seniority_fit: number;
  location_fit: number;
  recency: number;
}

export interface Match {
  id?: string;
  profile_id: string;
  job_id: string;
  score_total: number;
  score_breakdown: ScoreBreakdown;
  top_reasons: string[];
  gaps: string[];
  recommendations: string[];
  computed_at: string;
  embedding_model: string;
  posted_date?: string;
}

export interface MatchWithJob {
  match: Match;
  job: any; // Job object from job.ts
}

export interface MatchListResponse {
  matches: MatchWithJob[];
  total: number;
  page: number;
  per_page: number;
  message: string;
}

export interface MatchResponse {
  match: Match;
  job?: any;
  message: string;
}

export interface RecomputeMatchesResponse {
  matches_computed: number;
  profile_id: string;
  jobs_processed: number;
  message: string;
}
