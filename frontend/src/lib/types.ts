export type ProjectStatus = "pending" | "processing" | "completed" | "failed";
export type GuideStatus = "pending" | "processing" | "completed" | "failed";
export type TranscriptStatus = "uploaded" | "parsing" | "embedding" | "ready" | "failed";
export type AnalysisStatus = "pending" | "retrieving" | "classifying" | "generating" | "completed" | "failed";

export interface Project {
  id: string;
  name: string;
  objective: string | null;
  status: ProjectStatus;
  created_at: string;
  updated_at: string;
}

export interface InterviewGuide {
  id: string;
  project_id: string;
  source_file: string;
  status: GuideStatus;
  created_at: string;
  updated_at: string;
}

export interface ResearchQuestion {
  id: string;
  project_id: string;
  guide_id?: string;
  question_number: number;
  question_text: string;
  category: string | null;
  created_at: string;
}

export interface Expert {
  id: string;
  project_id: string;
  name: string;
  role: string | null;
  market: string | null;
  organization: string | null;
  created_at: string;
}

export interface Transcript {
  id: string;
  project_id: string;
  expert_id: string;
  file_name: string;
  file_path?: string;
  status: TranscriptStatus;
  duration?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Utterance {
  id: string;
  transcript_id: string;
  expert_id: string;
  speaker: string;
  text: string;
  timestamp_start: string | null;
  timestamp_end: string | null;
  sequence: number;
  created_at?: string;
}

export interface TimestampInfo {
  start: string | null;
  end: string | null;
}

export interface ExpertBrief {
  id: string;
  name: string;
  role?: string | null;
  market?: string | null;
}

export interface TranscriptBrief {
  id: string;
  file_name: string;
}

export interface Evidence {
  id: string;
  project_id?: string;
  question_id?: string;
  transcript_id?: string;
  expert_id?: string;
  utterance_id?: string;
  quote: string;
  topic?: string | null;
  relevance_score?: number | null;
  expert: ExpertBrief;
  transcript: TranscriptBrief;
  timestamp: TimestampInfo;
  created_at: string;
}

export interface Answer {
  id: string;
  project_id: string;
  question_id: string;
  expert_id: string;
  answer_text: string;
  status: AnalysisStatus;
  evidence: Evidence[];
  created_at: string;
  updated_at: string;
}

export interface DifferencePerspective {
  expert_id: string;
  expert_name: string;
  perspective: string;
}

export interface Difference {
  id: string;
  project_id: string;
  question_id: string;
  title: string | null;
  description: string | null;
  perspectives: DifferencePerspective[];
  evidence: Evidence[];
  created_at: string;
}

export interface Insight {
  id: string;
  project_id: string;
  question_id: string | null;
  title: string;
  summary: string;
  confidence: number | null;
  evidence: Evidence[];
  created_at: string;
}

export interface CopilotMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  evidence?: Evidence[];
  insufficient_evidence?: boolean;
  timestamp: string;
}
