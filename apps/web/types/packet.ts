export interface BulletSwap {
  role_index: number;
  original_bullet: string;
  suggested_bullet: string;
  evidence_ref?: string;
  reason: string;
}

export interface TailoringPlan {
  job_id: string;
  profile_id: string;
  summary_rewrite: string;
  skills_priority: string[];
  bullet_swaps: BulletSwap[];
  keyword_inserts: { [key: string]: string[] };
  gaps: string[];
  integrity_notes: string[];
  created_at: string;
  model_version: string;
}

export interface PacketFile {
  filename: string;
  filepath: string;
  content_hash: string;
  file_type: string;
  created_at: string;
}

export interface Packet {
  id?: string;
  job_id: string;
  profile_id: string;
  match_id?: string;
  tailoring_plan: TailoringPlan;
  cv_tex: PacketFile;
  cv_pdf?: PacketFile;
  cover_letter?: PacketFile;
  recruiter_message: PacketFile;
  common_answers: PacketFile;
  user_notes?: string;
  regeneration_count: number;
  created_at: string;
  updated_at: string;
}

export interface GeneratePacketRequest {
  job_id: string;
  include_cover_letter?: boolean;
  user_emphasis?: string[];
}

export interface PacketResponse {
  packet: Packet;
  message: string;
}

export interface PacketListResponse {
  packets: Packet[];
  total: number;
  page: number;
  per_page: number;
  message: string;
}
