/**
 * Interview preparation types matching backend schemas
 */

export type DifficultyLevel = 'easy' | 'medium' | 'hard';

export interface GroundingReference {
  experience_index: number;
  bullet_index?: number;
  evidence_text: string;
}

export interface STARStory {
  title: string;
  situation: string;
  task: string;
  action: string;
  result: string;
  skills_demonstrated: string[];
  grounding_refs: GroundingReference[];
}

export interface InterviewQuestion {
  question: string;
  category: string;
  reasoning: string;
}

export interface StudyResource {
  topic: string;
  resource_type: string;
  description: string;
}

export interface InterviewPack {
  id?: string;
  packet_id: string;
  job_id: string;
  profile_id: string;
  company_name: string;
  role_title: string;
  role_digest: string;
  company_digest: string;
  integrity_note?: string;
  plan_30_days: string[];
  plan_60_days: string[];
  plan_90_days: string[];
  star_stories: STARStory[];
  questions_to_ask: InterviewQuestion[];
  study_checklist: StudyResource[];
  generated_at: string;
  schema_version: string;
}

export interface TechnicalQuestion {
  question: string;
  difficulty: DifficultyLevel;
  answer: string;
  follow_ups: string[];
  key_concepts: string[];
}

export interface TechnicalQATopic {
  topic: string;
  questions: TechnicalQuestion[];
}

export interface TechnicalQA {
  id?: string;
  packet_id: string;
  job_id: string;
  profile_id: string;
  priority_topics: string[];
  topics: TechnicalQATopic[];
  generated_at: string;
  schema_version: string;
}

export interface InterviewPackResponse {
  interview_pack: InterviewPack;
  technical_qa: TechnicalQA;
  message: string;
}
