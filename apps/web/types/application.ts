// Application tracking types

export type ApplicationStatus =
  | 'prepared'
  | 'intent_created'
  | 'prefilling'
  | 'prefilled'
  | 'applied'
  | 'rejected'
  | 'interviewing'
  | 'offered'
  | 'accepted'
  | 'declined'
  | 'withdrawn';

export interface StatusHistoryEntry {
  status: ApplicationStatus;
  timestamp: string;
  note: string;
}

export interface Application {
  _id?: string;
  job_id: string;
  packet_id: string;
  profile_id: string;
  job_title: string;
  company_name: string;
  job_url: string;
  status: ApplicationStatus;
  status_history: StatusHistoryEntry[];
  prefill_intent_id?: string;
  prefill_log_id?: string;
  last_prefill_at?: string;
  notes: string;
  applied_at?: string;
  deadline?: string;
  created_at: string;
  updated_at: string;
}

export interface PrefillIntent {
  _id?: string;
  packet_id: string;
  job_url: string;
  user_fields: Record<string, any>;
  attachments: Record<string, string>;
  common_answers: Record<string, any>;
  auth_token?: string;
  token_expires_at?: string;
  status: string;
  created_at: string;
}

export interface PrefillIntentResponse {
  intent_id: string;
  auth_token: string;
  expires_at: string;
  message: string;
}

export interface FilledField {
  field_name: string;
  value: string;
  success: boolean;
  error?: string;
}

export interface PrefillError {
  field: string;
  error_message: string;
}

export interface PrefillLog {
  _id?: string;
  intent_id: string;
  detected_ats?: string;
  detection_confidence: number;
  filled_fields: FilledField[];
  missing_fields: string[];
  errors: PrefillError[];
  resume_attached: boolean;
  attachment_errors: string[];
  screenshot_paths: string[];
  timestamp: string;
  duration_seconds: number;
  stopped_before_submit: boolean;
  field_mappings: Record<string, any>;
}
