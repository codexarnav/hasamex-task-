import {
  Project,
  InterviewGuide,
  ResearchQuestion,
  Expert,
  Transcript,
  Utterance,
  Evidence,
  Answer,
  Difference,
  Insight,
  CopilotMessage,
} from "../types";

export const mockProject: Project = {
  id: "proj-1",
  name: "Robotic Surgery Adoption in European Hospitals",
  objective:
    "Evaluate clinical bottlenecks, capital procurement workflows, and reimbursement hurdles across UK, German, and French hospital systems.",
  status: "completed",
  created_at: "2026-09-20T10:00:00Z",
  updated_at: "2026-09-24T14:30:00Z",
};

export const mockProjectsList: Project[] = [
  mockProject,
  {
    id: "proj-2",
    name: "Cardiovascular AI Diagnostic Tool Clinical Viability",
    objective: "Assess radiologist acceptance and PACS integration requirements in Tier 1 US trauma centers.",
    status: "processing",
    created_at: "2026-09-22T08:15:00Z",
    updated_at: "2026-09-23T11:20:00Z",
  },
  {
    id: "proj-3",
    name: "Endoscopic Tele-Robotics in Ambulatory Surgery",
    objective: "Explore outpatient procedure economics and sterilization cycles in ambulatory surgical centers.",
    status: "pending",
    created_at: "2026-09-24T09:45:00Z",
    updated_at: "2026-09-24T09:45:00Z",
  },
];

export const mockGuide: InterviewGuide = {
  id: "guide-1",
  project_id: "proj-1",
  source_file: "surgical_robotics_interview_guide.pdf",
  status: "completed",
  created_at: "2026-09-20T10:05:00Z",
  updated_at: "2026-09-20T10:06:30Z",
};

export const mockQuestions: ResearchQuestion[] = [
  {
    id: "q-1",
    project_id: "proj-1",
    question_number: 1,
    question_text: "How would you describe current hospital adoption levels and primary evaluation criteria for robotic platforms?",
    category: "Current Adoption & Platform Evaluation",
    created_at: "2026-09-20T10:06:00Z",
  },
  {
    id: "q-2",
    project_id: "proj-1",
    question_number: 2,
    question_text: "What are the main operational and clinical barriers preventing wider adoption across surgical departments?",
    category: "Clinical Workflow & Adoption Barriers",
    created_at: "2026-09-20T10:06:00Z",
  },
  {
    id: "q-3",
    project_id: "proj-1",
    question_number: 3,
    question_text: "How do capital procurement and total cost of ownership considerations shape purchasing decisions?",
    category: "Procurement & Economics",
    created_at: "2026-09-20T10:06:00Z",
  },
  {
    id: "q-4",
    project_id: "proj-1",
    question_number: 4,
    question_text: "What are the surgeon training requirements, learning curves, and simulator certification protocols?",
    category: "Training & Learning Curves",
    created_at: "2026-09-20T10:06:00Z",
  },
  {
    id: "q-5",
    project_id: "proj-1",
    question_number: 5,
    question_text: "How do national reimbursement schemes and statutory health insurance impact adoption timelines?",
    category: "Reimbursement & Regulatory",
    created_at: "2026-09-20T10:06:00Z",
  },
  {
    id: "q-6",
    project_id: "proj-1",
    question_number: 6,
    question_text: "What future indications and technological enhancements are most requested by surgical teams?",
    category: "Future Outlook & Indications",
    created_at: "2026-09-20T10:06:00Z",
  },
];

export const mockExperts: Expert[] = [
  {
    id: "exp-1",
    project_id: "proj-1",
    name: "Dr. Emily Carter",
    role: "Consultant Urologist & Robotic Lead",
    market: "UK",
    organization: "Imperial College Healthcare NHS Trust",
    created_at: "2026-09-20T10:15:00Z",
  },
  {
    id: "exp-2",
    project_id: "proj-1",
    name: "Anna Keller",
    role: "Former Hospital Procurement Director",
    market: "Germany",
    organization: "Charité – Universitätsmedizin Berlin",
    created_at: "2026-09-20T10:16:00Z",
  },
  {
    id: "exp-3",
    project_id: "proj-1",
    name: "Dr. Jean Martin",
    role: "Head of Urology Department",
    market: "France",
    organization: "Hôpital Européen Georges-Pompidou (AP-HP)",
    created_at: "2026-09-20T10:17:00Z",
  },
];

export const mockTranscripts: Transcript[] = [
  {
    id: "tr-1",
    project_id: "proj-1",
    expert_id: "exp-1",
    file_name: "UK_Expert_Dr_Emily_Carter.txt",
    file_path: "proj-1/uk_expert.txt",
    status: "ready",
    duration: "45 mins",
    created_at: "2026-09-20T10:20:00Z",
    updated_at: "2026-09-20T10:22:00Z",
  },
  {
    id: "tr-2",
    project_id: "proj-1",
    expert_id: "exp-2",
    file_name: "Germany_Expert_Anna_Keller.txt",
    file_path: "proj-1/germany_expert.txt",
    status: "ready",
    duration: "52 mins",
    created_at: "2026-09-20T10:25:00Z",
    updated_at: "2026-09-20T10:27:00Z",
  },
  {
    id: "tr-3",
    project_id: "proj-1",
    expert_id: "exp-3",
    file_name: "France_Expert_Dr_Jean_Martin.txt",
    file_path: "proj-1/france_expert.txt",
    status: "ready",
    duration: "48 mins",
    created_at: "2026-09-20T10:30:00Z",
    updated_at: "2026-09-20T10:32:00Z",
  },
];

export const mockUtterances: Utterance[] = [
  {
    id: "utt-1",
    transcript_id: "tr-1",
    expert_id: "exp-1",
    speaker: "Interviewer",
    text: "What are the main operational and clinical barriers preventing wider robotic adoption in your department?",
    timestamp_start: "00:17:52",
    timestamp_end: "00:18:02",
    sequence: 24,
  },
  {
    id: "utt-2",
    transcript_id: "tr-1",
    expert_id: "exp-1",
    speaker: "Dr. Emily Carter",
    text: "There are several considerations, but nursing and theater staff cross-training is by far the primary operational hurdle. Dedicated theater time must be blocked out for two weeks.",
    timestamp_start: "00:18:03",
    timestamp_end: "00:18:40",
    sequence: 25,
  },
  {
    id: "utt-3",
    transcript_id: "tr-1",
    expert_id: "exp-1",
    speaker: "Dr. Emily Carter",
    text: "Training capacity is one of the biggest practical limitations. If you have only one console, you cannot train junior surgeons while running active lists without lengthening overall operating times.",
    timestamp_start: "00:18:42",
    timestamp_end: "00:19:15",
    sequence: 26,
  },
  {
    id: "utt-4",
    transcript_id: "tr-1",
    expert_id: "exp-1",
    speaker: "Dr. Emily Carter",
    text: "From a business perspective, the NHS Trust requires a robust business case demonstrating reduced length of stay to justify the initial capital outlay.",
    timestamp_start: "00:19:18",
    timestamp_end: "00:19:48",
    sequence: 27,
  },
  {
    id: "utt-5",
    transcript_id: "tr-2",
    expert_id: "exp-2",
    speaker: "Anna Keller",
    text: "In Germany, DRG reimbursement codes cover standard laparoscopic surgery, but the incremental per-procedure consumable cost of robotic instruments is not fully refunded by statutory health funds.",
    timestamp_start: "00:26:40",
    timestamp_end: "00:27:10",
    sequence: 31,
  },
  {
    id: "utt-6",
    transcript_id: "tr-2",
    expert_id: "exp-2",
    speaker: "Anna Keller",
    text: "The training investment is substantial, but hospital administration worries primarily about instrument sterilization turnaround times and recurrent maintenance agreements.",
    timestamp_start: "00:27:13",
    timestamp_end: "00:27:48",
    sequence: 32,
  },
  {
    id: "utt-7",
    transcript_id: "tr-3",
    expert_id: "exp-3",
    speaker: "Dr. Jean Martin",
    text: "In France, public hospitals face strict annual investment caps. We often form regional purchasing consortia to negotiate multi-hospital leasing packages rather than direct capital purchases.",
    timestamp_start: "00:14:22",
    timestamp_end: "00:15:00",
    sequence: 18,
  },
  {
    id: "utt-8",
    transcript_id: "tr-3",
    expert_id: "exp-3",
    speaker: "Dr. Jean Martin",
    text: "Surgeon enthusiasm is very high, but scheduling conflicts in shared multidisciplinary operating rooms limit weekly case throughput.",
    timestamp_start: "00:15:05",
    timestamp_end: "00:15:35",
    sequence: 19,
  },
];

export const mockEvidenceList: Evidence[] = [
  {
    id: "ev-1",
    project_id: "proj-1",
    question_id: "q-2",
    transcript_id: "tr-1",
    expert_id: "exp-1",
    utterance_id: "utt-3",
    quote:
      "Training capacity is one of the biggest practical limitations. If you have only one console, you cannot train junior surgeons while running active lists without lengthening overall operating times.",
    topic: "Surgeon & Staff Training",
    relevance_score: 0.98,
    expert: {
      id: "exp-1",
      name: "Dr. Emily Carter",
      role: "Consultant Urologist & Robotic Lead",
      market: "UK",
    },
    transcript: {
      id: "tr-1",
      file_name: "UK_Expert_Dr_Emily_Carter.txt",
    },
    timestamp: {
      start: "00:18:42",
      end: "00:19:15",
    },
    created_at: "2026-09-24T14:31:00Z",
  },
  {
    id: "ev-2",
    project_id: "proj-1",
    question_id: "q-2",
    transcript_id: "tr-1",
    expert_id: "exp-1",
    utterance_id: "utt-2",
    quote:
      "There are several considerations, but nursing and theater staff cross-training is by far the primary operational hurdle. Dedicated theater time must be blocked out for two weeks.",
    topic: "Nursing Workflow",
    relevance_score: 0.95,
    expert: {
      id: "exp-1",
      name: "Dr. Emily Carter",
      role: "Consultant Urologist & Robotic Lead",
      market: "UK",
    },
    transcript: {
      id: "tr-1",
      file_name: "UK_Expert_Dr_Emily_Carter.txt",
    },
    timestamp: {
      start: "00:18:03",
      end: "00:18:40",
    },
    created_at: "2026-09-24T14:31:00Z",
  },
  {
    id: "ev-3",
    project_id: "proj-1",
    question_id: "q-2",
    transcript_id: "tr-2",
    expert_id: "exp-2",
    utterance_id: "utt-6",
    quote:
      "The training investment is substantial, but hospital administration worries primarily about instrument sterilization turnaround times and recurrent maintenance agreements.",
    topic: "Sterilization & Maintenance",
    relevance_score: 0.94,
    expert: {
      id: "exp-2",
      name: "Anna Keller",
      role: "Former Hospital Procurement Director",
      market: "Germany",
    },
    transcript: {
      id: "tr-2",
      file_name: "Germany_Expert_Anna_Keller.txt",
    },
    timestamp: {
      start: "00:27:13",
      end: "00:27:48",
    },
    created_at: "2026-09-24T14:31:10Z",
  },
  {
    id: "ev-4",
    project_id: "proj-1",
    question_id: "q-2",
    transcript_id: "tr-3",
    expert_id: "exp-3",
    utterance_id: "utt-8",
    quote:
      "Surgeon enthusiasm is very high, but scheduling conflicts in shared multidisciplinary operating rooms limit weekly case throughput.",
    topic: "Operating Room Scheduling",
    relevance_score: 0.91,
    expert: {
      id: "exp-3",
      name: "Dr. Jean Martin",
      role: "Head of Urology Department",
      market: "France",
    },
    transcript: {
      id: "tr-3",
      file_name: "France_Expert_Dr_Jean_Martin.txt",
    },
    timestamp: {
      start: "00:15:05",
      end: "00:15:35",
    },
    created_at: "2026-09-24T14:31:20Z",
  },
  {
    id: "ev-5",
    project_id: "proj-1",
    question_id: "q-3",
    transcript_id: "tr-1",
    expert_id: "exp-1",
    utterance_id: "utt-4",
    quote:
      "From a business perspective, the NHS Trust requires a robust business case demonstrating reduced length of stay to justify the initial capital outlay.",
    topic: "NHS Capital Case",
    relevance_score: 0.96,
    expert: {
      id: "exp-1",
      name: "Dr. Emily Carter",
      role: "Consultant Urologist & Robotic Lead",
      market: "UK",
    },
    transcript: {
      id: "tr-1",
      file_name: "UK_Expert_Dr_Emily_Carter.txt",
    },
    timestamp: {
      start: "00:19:18",
      end: "00:19:48",
    },
    created_at: "2026-09-24T14:31:30Z",
  },
  {
    id: "ev-6",
    project_id: "proj-1",
    question_id: "q-3",
    transcript_id: "tr-2",
    expert_id: "exp-2",
    utterance_id: "utt-5",
    quote:
      "In Germany, DRG reimbursement codes cover standard laparoscopic surgery, but the incremental per-procedure consumable cost of robotic instruments is not fully refunded by statutory health funds.",
    topic: "German DRG Gaps",
    relevance_score: 0.97,
    expert: {
      id: "exp-2",
      name: "Anna Keller",
      role: "Former Hospital Procurement Director",
      market: "Germany",
    },
    transcript: {
      id: "tr-2",
      file_name: "Germany_Expert_Anna_Keller.txt",
    },
    timestamp: {
      start: "00:26:40",
      end: "00:27:10",
    },
    created_at: "2026-09-24T14:31:40Z",
  },
  {
    id: "ev-7",
    project_id: "proj-1",
    question_id: "q-3",
    transcript_id: "tr-3",
    expert_id: "exp-3",
    utterance_id: "utt-7",
    quote:
      "In France, public hospitals face strict annual investment caps. We often form regional purchasing consortia to negotiate multi-hospital leasing packages rather than direct capital purchases.",
    topic: "French Leasing Models",
    relevance_score: 0.95,
    expert: {
      id: "exp-3",
      name: "Dr. Jean Martin",
      role: "Head of Urology Department",
      market: "France",
    },
    transcript: {
      id: "tr-3",
      file_name: "France_Expert_Dr_Jean_Martin.txt",
    },
    timestamp: {
      start: "00:14:22",
      end: "00:15:00",
    },
    created_at: "2026-09-24T14:31:50Z",
  },
];

export const mockAnswersQ2: Answer[] = [
  {
    id: "ans-1",
    project_id: "proj-1",
    question_id: "q-2",
    expert_id: "exp-1",
    answer_text:
      "In the UK, operational adoption is primarily constrained by nursing staff cross-training requirements (requiring up to two weeks of dedicated theater time) and limited console access that restricts simulator training for junior clinicians without disrupting active surgical lists.",
    status: "completed",
    evidence: [mockEvidenceList[0], mockEvidenceList[1]],
    created_at: "2026-09-24T14:32:00Z",
    updated_at: "2026-09-24T14:32:00Z",
  },
  {
    id: "ans-2",
    project_id: "proj-1",
    question_id: "q-2",
    expert_id: "exp-2",
    answer_text:
      "In Germany, operational friction is concentrated on central sterilization turnaround times for multi-jointed robotic instruments, as well as the substantial financial overhead of recurrent service contracts.",
    status: "completed",
    evidence: [mockEvidenceList[2]],
    created_at: "2026-09-24T14:32:00Z",
    updated_at: "2026-09-24T14:32:00Z",
  },
  {
    id: "ans-3",
    project_id: "proj-1",
    question_id: "q-2",
    expert_id: "exp-3",
    answer_text:
      "In France, surgeon adoption and enthusiasm are high, but departmental scheduling constraints in shared multidisciplinary operating rooms restrict weekly procedure throughput.",
    status: "completed",
    evidence: [mockEvidenceList[3]],
    created_at: "2026-09-24T14:32:00Z",
    updated_at: "2026-09-24T14:32:00Z",
  },
];

export const mockDifferences: Difference[] = [
  {
    id: "diff-1",
    project_id: "proj-1",
    question_id: "q-3",
    title: "Capital Procurement Models & Reimbursement Structure",
    description:
      "Substantial divergence exists in financing pathways: UK centers prioritize length-of-stay reduction in NHS board business cases, Germany struggles with DRG reimbursement gaps for consumables, and French hospitals rely on regional leasing consortia.",
    perspectives: [
      {
        expert_id: "exp-1",
        expert_name: "Dr. Emily Carter (UK)",
        perspective: "NHS Trust requires proven reduction in hospital bed days to approve direct capital allocations.",
      },
      {
        expert_id: "exp-2",
        expert_name: "Anna Keller (Germany)",
        perspective: "Statutory DRG tariff covers standard laparoscopy, leaving per-case consumable deltas as an uncompensated hospital expense.",
      },
      {
        expert_id: "exp-3",
        expert_name: "Dr. Jean Martin (France)",
        perspective: "Strict public CapEx ceilings drive multi-hospital regional leasing consortia rather than direct purchases.",
      },
    ],
    evidence: [mockEvidenceList[4], mockEvidenceList[5], mockEvidenceList[6]],
    created_at: "2026-09-24T14:33:00Z",
  },
  {
    id: "diff-2",
    project_id: "proj-1",
    question_id: "q-2",
    title: "Primary Operational Bottlenecks",
    description:
      "Operational constraints vary from staff training in the UK to sterilization logistics in Germany and multidisciplinary OR scheduling bottlenecks in France.",
    perspectives: [
      {
        expert_id: "exp-1",
        expert_name: "Dr. Emily Carter (UK)",
        perspective: "Nursing and theater staff cross-training capacity.",
      },
      {
        expert_id: "exp-2",
        expert_name: "Anna Keller (Germany)",
        perspective: "Central sterilization unit turnaround times and maintenance agreements.",
      },
      {
        expert_id: "exp-3",
        expert_name: "Dr. Jean Martin (France)",
        perspective: "Inter-departmental OR scheduling competition.",
      },
    ],
    evidence: [mockEvidenceList[0], mockEvidenceList[2], mockEvidenceList[3]],
    created_at: "2026-09-24T14:33:10Z",
  },
];

export const mockInsights: Insight[] = [
  {
    id: "ins-1",
    project_id: "proj-1",
    question_id: "q-2",
    title: "Training capacity is a recurring clinical adoption barrier",
    summary:
      "Across all interviewed markets, training requirements for both surgeons and theater nurses represent the initial deployment bottleneck, with single-console hospitals experiencing trade-offs between training and clinical throughput.",
    confidence: 0.94,
    evidence: [mockEvidenceList[0], mockEvidenceList[1], mockEvidenceList[2]],
    created_at: "2026-09-24T14:34:00Z",
  },
  {
    id: "ins-2",
    project_id: "proj-1",
    question_id: "q-3",
    title: "Capital budget constraints drive divergent acquisition mechanisms",
    summary:
      "Direct capital purchase is becoming less common in Western European public health systems, with hospitals increasingly adopting structured operational leases, consumable bundling, and regional buying consortia to bypass CapEx limits.",
    confidence: 0.91,
    evidence: [mockEvidenceList[4], mockEvidenceList[5], mockEvidenceList[6]],
    created_at: "2026-09-24T14:34:10Z",
  },
  {
    id: "ins-3",
    project_id: "proj-1",
    question_id: null,
    title: "Consumable cost reimbursement remains the key long-term margin pressure",
    summary:
      "While upfront system placement can be restructured via leasing, the unreimbursed per-case margin compression from disposable robotic instruments limits utilization to high-complexity oncology procedures.",
    confidence: 0.88,
    evidence: [mockEvidenceList[4], mockEvidenceList[5]],
    created_at: "2026-09-24T14:34:20Z",
  },
];

export const mockCopilotInitialMessages: CopilotMessage[] = [
  {
    id: "msg-1",
    role: "user",
    content: "What are the strongest barriers to adoption across the interview transcripts?",
    timestamp: "2026-09-24T14:35:00Z",
  },
  {
    id: "msg-2",
    role: "assistant",
    content:
      "The interview transcripts repeatedly emphasize three interconnected adoption barriers:\n\n1. **Staff & Surgeon Training Capacity:** Dr. Emily Carter highlighted that single-console limitations force a trade-off between live surgical lists and junior surgeon simulator training.\n2. **Financial & Consumable Overhead:** Anna Keller noted that German statutory reimbursement codes do not cover the incremental consumable costs, putting pressure on department budgets.\n3. **Operating Room Scheduling & Logistics:** Dr. Jean Martin cited scheduling friction in shared multidisciplinary operating theaters as a barrier to case volume.",
    evidence: [mockEvidenceList[0], mockEvidenceList[2], mockEvidenceList[3]],
    insufficient_evidence: false,
    timestamp: "2026-09-24T14:35:10Z",
  },
];
