import {
  Project,
  ResearchQuestion,
  Expert,
  Transcript,
  Utterance,
  Evidence,
  Answer,
  Difference,
  Insight,
  CopilotMessage,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiError extends Error {
  status: number;
  detail?: string;

  constructor(message: string, status: number, detail?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorDetail = "";
    try {
      const errorJson = await response.json();
      errorDetail =
        errorJson.detail || errorJson.error || JSON.stringify(errorJson);
    } catch {
      errorDetail = await response.text();
    }
    throw new ApiError(
      `Request failed with status ${response.status}`,
      response.status,
      errorDetail
    );
  }
  return response.json();
}

export const api = {
  // Health
  async getHealth(): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE_URL}/health`);
    return handleResponse<{ status: string }>(res);
  },

  // Projects
  async getProjects(skip = 0, limit = 50): Promise<{ projects: Project[]; total: number }> {
    const res = await fetch(`${API_BASE_URL}/projects?skip=${skip}&limit=${limit}`, {
      cache: "no-store",
    });
    return handleResponse<{ projects: Project[]; total: number }>(res);
  },

  async getProject(projectId: string): Promise<Project> {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
      cache: "no-store",
    });
    return handleResponse<Project>(res);
  },

  async createProject(data: { name: string; objective?: string | null }): Promise<Project> {
    const res = await fetch(`${API_BASE_URL}/projects`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    return handleResponse<Project>(res);
  },

  // Interview Guide & Questions
  async uploadGuide(
    projectId: string,
    file: File
  ): Promise<{ questions: ResearchQuestion[]; total: number }> {
    const formData = new FormData();
    formData.append("file", file);

    // Note: Do NOT set Content-Type header so browser computes the boundary automatically
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/guide`, {
      method: "POST",
      body: formData,
    });
    return handleResponse<{ questions: ResearchQuestion[]; total: number }>(res);
  },

  async getQuestions(
    projectId: string
  ): Promise<{ questions: ResearchQuestion[]; total: number }> {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/questions`, {
      cache: "no-store",
    });
    return handleResponse<{ questions: ResearchQuestion[]; total: number }>(res);
  },

  // Experts
  async getExperts(projectId: string): Promise<{ experts: Expert[]; total: number }> {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/experts`, {
      cache: "no-store",
    });
    return handleResponse<{ experts: Expert[]; total: number }>(res);
  },

  async createExpert(
    projectId: string,
    data: {
      name: string;
      role?: string | null;
      market?: string | null;
      organization?: string | null;
    }
  ): Promise<Expert> {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/experts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    return handleResponse<Expert>(res);
  },

  // Transcripts & Utterances
  async uploadTranscript(
    projectId: string,
    expertId: string,
    file: File
  ): Promise<Transcript> {
    const formData = new FormData();
    formData.append("expert_id", expertId);
    formData.append("file", file);

    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/transcripts`, {
      method: "POST",
      body: formData,
    });
    return handleResponse<Transcript>(res);
  },

  async getTranscripts(
    projectId: string
  ): Promise<{ transcripts: Transcript[]; total: number }> {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/transcripts`, {
      cache: "no-store",
    });
    return handleResponse<{ transcripts: Transcript[]; total: number }>(res);
  },

  async getTranscriptDetail(
    transcriptId: string
  ): Promise<Transcript & { utterance_count: number }> {
    const res = await fetch(`${API_BASE_URL}/transcripts/${transcriptId}`, {
      cache: "no-store",
    });
    return handleResponse<Transcript & { utterance_count: number }>(res);
  },

  async getTranscriptUtterances(
    transcriptId: string
  ): Promise<{ transcript_id: string; utterances: Utterance[]; total: number }> {
    const res = await fetch(`${API_BASE_URL}/transcripts/${transcriptId}/utterances`, {
      cache: "no-store",
    });
    return handleResponse<{ transcript_id: string; utterances: Utterance[]; total: number }>(
      res
    );
  },

  async deleteTranscript(transcriptId: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/transcripts/${transcriptId}`, {
      method: "DELETE",
    });
    if (!res.ok && res.status !== 204) {
      return handleResponse<void>(res);
    }
  },

  // Analysis Pipeline & Grounded Answers
  async runAnalysis(
    projectId: string,
    transcriptIds?: string[]
  ): Promise<{
    project_id: string;
    status: string;
    questions: {
      question_id: string;
      question_number: number;
      question_text: string;
      answers: Answer[];
    }[];
  }> {
    const fetchOptions: RequestInit = {
      method: "POST",
    };
    if (transcriptIds && transcriptIds.length > 0) {
      fetchOptions.headers = { "Content-Type": "application/json" };
      fetchOptions.body = JSON.stringify({ transcript_ids: transcriptIds });
    }
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/analysis`, fetchOptions);
    return handleResponse<{
      project_id: string;
      status: string;
      questions: {
        question_id: string;
        question_number: number;
        question_text: string;
        answers: Answer[];
      }[];
    }>(res);
  },

  async getAnalysis(
    projectId: string
  ): Promise<{
    project_id: string;
    status: string;
    questions: {
      question_id: string;
      question_number: number;
      question_text: string;
      answers: Answer[];
    }[];
  }> {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/analysis`, {
      cache: "no-store",
    });
    return handleResponse<{
      project_id: string;
      status: string;
      questions: {
        question_id: string;
        question_number: number;
        question_text: string;
        answers: Answer[];
      }[];
    }>(res);
  },

  async getQuestionAnalysis(
    projectId: string,
    questionId: string
  ): Promise<{
    question_id: string;
    question_number: number;
    question_text: string;
    answers: Answer[];
  }> {
    const res = await fetch(
      `${API_BASE_URL}/projects/${projectId}/analysis/${questionId}`,
      { cache: "no-store" }
    );
    return handleResponse<{
      question_id: string;
      question_number: number;
      question_text: string;
      answers: Answer[];
    }>(res);
  },

  // Evidence
  async getEvidenceList(
    projectId: string
  ): Promise<{ evidence: Evidence[]; total: number }> {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/evidence`, {
      cache: "no-store",
    });
    return handleResponse<{ evidence: Evidence[]; total: number }>(res);
  },

  async getEvidence(evidenceId: string): Promise<Evidence> {
    const res = await fetch(`${API_BASE_URL}/evidence/${evidenceId}`, {
      cache: "no-store",
    });
    return handleResponse<Evidence>(res);
  },

  // Differences
  async getDifferences(
    projectId: string
  ): Promise<{ differences: Difference[]; total: number }> {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/differences`, {
      cache: "no-store",
    });
    return handleResponse<{ differences: Difference[]; total: number }>(res);
  },

  // Insights
  async getInsights(
    projectId: string
  ): Promise<{ insights: Insight[]; total: number }> {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/insights`, {
      cache: "no-store",
    });
    return handleResponse<{ insights: Insight[]; total: number }>(res);
  },

  // Copilot
  async askCopilot(
    projectId: string,
    question: string
  ): Promise<{
    answer: string;
    evidence: Evidence[];
    insufficient_evidence: boolean;
  }> {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });
    return handleResponse<{
      answer: string;
      evidence: Evidence[];
      insufficient_evidence: boolean;
    }>(res);
  },
};
