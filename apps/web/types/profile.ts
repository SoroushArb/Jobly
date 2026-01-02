export interface Preferences {
  europe: boolean;
  remote: boolean;
  countries: string[];
  cities: string[];
  skill_tags: string[];
  role_tags: string[];
  visa_required: boolean | null;
  languages: string[];
}

export interface ExperienceBullet {
  text: string;
  evidence_ref?: string;
}

export interface ExperienceRole {
  company: string;
  title: string;
  dates: string;
  bullets: ExperienceBullet[];
  tech: string[];
}

export interface SkillGroup {
  category: string;
  skills: string[];
}

export interface Project {
  name: string;
  description?: string;
  tech: string[];
  url?: string;
}

export interface Education {
  institution: string;
  degree?: string;
  field?: string;
  dates?: string;
  details: string[];
}

export interface UserProfile {
  name: string;
  email: string;
  links: string[];
  summary?: string;
  skills: SkillGroup[];
  experience: ExperienceRole[];
  projects: Project[];
  education: Education[];
  preferences: Preferences;
  schema_version: string;
  updated_at: string;
}

export interface UploadCVResponse {
  extracted_text: string;
  draft_profile: UserProfile;
  message: string;
}

export interface ProfileResponse {
  profile: UserProfile;
  message: string;
}

export interface ProfileSaveResponse {
  profile_id: string;
  message: string;
}

export interface CVDocument {
  id?: string;
  user_email: string;
  filename: string;
  extracted_text: string;
  parsed_profile: UserProfile;
  is_active: boolean;
  upload_date: string;
}

export interface CVListResponse {
  cvs: CVDocument[];
  total: number;
  message: string;
}
