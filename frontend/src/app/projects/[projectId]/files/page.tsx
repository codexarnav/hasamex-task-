"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { ProjectHeader } from "@/components/layout/ProjectHeader";
import { FileCard } from "@/components/domain/FileCard";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import {
  Project,
  Expert,
  Transcript,
  ResearchQuestion,
} from "@/lib/types";
import { api } from "@/lib/api";
import {
  Upload,
  Plus,
  Play,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Loader2,
  FileText,
  HelpCircle,
  ArrowRight,
} from "lucide-react";

export default function FilesPage({ params }: { params: { projectId: string } }) {
  const { projectId } = params;

  // Data states
  const [project, setProject] = useState<Project | null>(null);
  const [experts, setExperts] = useState<Expert[]>([]);
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [questions, setQuestions] = useState<ResearchQuestion[]>([]);
  const [guideFileName, setGuideFileName] = useState<string | null>(null);

  // Loading & Error states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal open states
  const [guideModalOpen, setGuideModalOpen] = useState(false);
  const [transcriptModalOpen, setTranscriptModalOpen] = useState(false);
  const [expertModalOpen, setExpertModalOpen] = useState(false);

  // Form states - Guide
  const [selectedGuideFile, setSelectedGuideFile] = useState<File | null>(null);
  const [guideUploading, setGuideUploading] = useState(false);
  const [guideError, setGuideError] = useState<string | null>(null);
  const guideInputRef = useRef<HTMLInputElement>(null);

  // Form states - Expert
  const [expertName, setExpertName] = useState("");
  const [expertRole, setExpertRole] = useState("");
  const [expertMarket, setExpertMarket] = useState("UK");
  const [expertOrg, setExpertOrg] = useState("");
  const [expertSubmitting, setExpertSubmitting] = useState(false);
  const [expertError, setExpertError] = useState<string | null>(null);

  // Form states - Transcript
  const [selectedExpertId, setSelectedExpertId] = useState("");
  const [selectedTranscriptFile, setSelectedTranscriptFile] = useState<File | null>(null);
  const [transcriptUploading, setTranscriptUploading] = useState(false);
  const [transcriptError, setTranscriptError] = useState<string | null>(null);
  const transcriptInputRef = useRef<HTMLInputElement>(null);

  // Transcript selection state
  const [selectedTranscriptIds, setSelectedTranscriptIds] = useState<Set<string>>(new Set());

  // Analysis state
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [analysisSuccess, setAnalysisSuccess] = useState<string | null>(null);

  const toggleTranscriptSelection = (id: string) => {
    setSelectedTranscriptIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const selectAllTranscripts = () => {
    const readyIds = transcripts.filter((t) => t.status === "ready").map((t) => t.id);
    setSelectedTranscriptIds(new Set(readyIds));
  };

  const deselectAllTranscripts = () => {
    setSelectedTranscriptIds(new Set());
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [projRes, expRes, transRes, qRes] = await Promise.allSettled([
        api.getProject(projectId),
        api.getExperts(projectId),
        api.getTranscripts(projectId),
        api.getQuestions(projectId),
      ]);

      if (projRes.status === "fulfilled") {
        setProject(projRes.value);
      }
      if (expRes.status === "fulfilled") {
        setExperts(expRes.value.experts || []);
        if (expRes.value.experts?.length > 0 && !selectedExpertId) {
          setSelectedExpertId(expRes.value.experts[0].id);
        }
      }
      if (transRes.status === "fulfilled") {
        setTranscripts(transRes.value.transcripts || []);
      }
      if (qRes.status === "fulfilled") {
        setQuestions(qRes.value.questions || []);
      }
    } catch (err: any) {
      setError(err.detail || err.message || "Failed to load project files");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [projectId]);

  // Handle Guide Upload
  const handleUploadGuide = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedGuideFile) {
      setGuideError("Please choose a file to upload");
      return;
    }

    try {
      setGuideUploading(true);
      setGuideError(null);
      const res = await api.uploadGuide(projectId, selectedGuideFile);
      setQuestions(res.questions || []);
      setGuideFileName(selectedGuideFile.name);
      setGuideModalOpen(false);
      setSelectedGuideFile(null);
      await fetchData();
    } catch (err: any) {
      setGuideError(err.detail || err.message || "Failed to upload and extract guide");
    } finally {
      setGuideUploading(false);
    }
  };

  // Handle Expert Registration
  const handleCreateExpert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!expertName.trim()) {
      setExpertError("Expert full name is required");
      return;
    }

    try {
      setExpertSubmitting(true);
      setExpertError(null);
      const newExp = await api.createExpert(projectId, {
        name: expertName.trim(),
        role: expertRole.trim() || null,
        market: expertMarket.trim() || null,
        organization: expertOrg.trim() || null,
      });
      setExperts((prev) => [...prev, newExp]);
      setSelectedExpertId(newExp.id);
      setExpertName("");
      setExpertRole("");
      setExpertOrg("");
      setExpertModalOpen(false);
    } catch (err: any) {
      setExpertError(err.detail || err.message || "Failed to register expert");
    } finally {
      setExpertSubmitting(false);
    }
  };

  // Handle Transcript Upload
  const handleUploadTranscript = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedExpertId) {
      setTranscriptError("Please select or register an expert first");
      return;
    }
    if (!selectedTranscriptFile) {
      setTranscriptError("Please choose a transcript file (.txt, .pdf)");
      return;
    }

    try {
      setTranscriptUploading(true);
      setTranscriptError(null);
      const newTranscript = await api.uploadTranscript(
        projectId,
        selectedExpertId,
        selectedTranscriptFile
      );
      setTranscripts((prev) => [newTranscript, ...prev]);
      setTranscriptModalOpen(false);
      setSelectedTranscriptFile(null);
      await fetchData();
    } catch (err: any) {
      setTranscriptError(err.detail || err.message || "Failed to upload and ingest transcript");
    } finally {
      setTranscriptUploading(false);
    }
  };

  // Handle Delete Transcript
  const handleDeleteTranscript = async (transcriptId: string) => {
    if (!window.confirm("Are you sure you want to delete this transcript? This will remove its indexed utterances.")) {
      return;
    }
    try {
      await api.deleteTranscript(transcriptId);
      setTranscripts((prev) => prev.filter((t) => t.id !== transcriptId));
      await fetchData();
    } catch (err: any) {
      alert(err.detail || err.message || "Failed to delete transcript");
    }
  };

  // Handle Trigger Full Analysis
  const handleRunAnalysis = async (transcriptIds?: string[]) => {
    if (questions.length === 0) {
      setAnalysisError("Please upload an interview guide first so questions can be extracted.");
      return;
    }
    if (transcripts.length === 0) {
      setAnalysisError("Please upload at least one expert transcript before running analysis.");
      return;
    }

    const idsToAnalyze = transcriptIds || (selectedTranscriptIds.size > 0 ? Array.from(selectedTranscriptIds) : undefined);

    try {
      setAnalyzing(true);
      setAnalysisError(null);
      setAnalysisSuccess(null);

      const res = await api.runAnalysis(projectId, idsToAnalyze);
      const scope = idsToAnalyze ? `${idsToAnalyze.length} selected transcript(s)` : "all transcripts";
      setAnalysisSuccess(`Analysis completed across ${res.questions?.length || questions.length} questions for ${scope}!`);
      await fetchData();
    } catch (err: any) {
      setAnalysisError(err.detail || err.message || "Qualitative analysis run failed");
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return <LoadingState message="Loading project files and expert data..." />;
  }

  if (error) {
    return (
      <ErrorState
        title="Could not load project files"
        message={error}
        onRetry={fetchData}
      />
    );
  }

  const expertMap = new Map(experts.map((e) => [e.id, e]));

  return (
    <div className="space-y-8 pb-12">
      <ProjectHeader
        title="Project Files & Data"
        description="Manage the interview guide, registered expert profiles, and uploaded transcript recordings."
        actions={
          <Button
            size="sm"
            onClick={() => handleRunAnalysis()}
            disabled={analyzing}
            className="flex items-center gap-1.5 shadow-sm"
          >
            {analyzing ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin fill-current" />
                <span>Analyzing Pipeline...</span>
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 fill-current" />
                <span>
                  {selectedTranscriptIds.size > 0
                    ? `Analyze ${selectedTranscriptIds.size} Selected`
                    : "Run Analysis"}
                </span>
              </>
            )}
          </Button>
        }
      />

      {/* Analysis Notifications */}
      {analysisError && (
        <div className="flex items-start gap-2.5 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs">
          <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-rose-600" />
          <div className="space-y-1">
            <div className="font-semibold">Analysis Pipeline Error</div>
            <div>{analysisError}</div>
          </div>
        </div>
      )}

      {analysisSuccess && (
        <div className="flex items-center justify-between p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600" />
            <span className="font-medium">{analysisSuccess}</span>
          </div>
          <Link
            href={`/projects/${projectId}/questions`}
            className="inline-flex items-center gap-1 font-semibold text-emerald-900 underline hover:no-underline"
          >
            <span>View Grounded Answers</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      )}

      {/* 1. Interview Guide Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              1. Interview Guide
            </h2>
            <p className="text-xs text-muted-foreground">
              The research instrument used to extract questions dynamically via Gemini.
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setGuideError(null);
              setGuideModalOpen(true);
            }}
            className="text-xs flex items-center gap-1.5"
          >
            <Upload className="h-3.5 w-3.5" />
            <span>Upload Guide</span>
          </Button>
        </div>

        {questions.length > 0 ? (
          <div className="rounded-xl border border-border bg-card p-5 shadow-2xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-700">
                  <FileText className="h-5 w-5" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-foreground">
                    {guideFileName || "Research Interview Guide"}
                  </div>
                  <div className="text-xs text-emerald-600 font-medium flex items-center gap-1 mt-0.5">
                    <CheckCircle2 className="h-3 w-3" />
                    <span>{questions.length} research questions extracted and persisted</span>
                  </div>
                </div>
              </div>
              <Link
                href={`/projects/${projectId}/questions`}
                className="text-xs text-slate-700 hover:text-slate-900 font-medium underline"
              >
                View Questions
              </Link>
            </div>
          </div>
        ) : (
          <div className="rounded-xl border border-dashed border-border bg-slate-50/50 p-6 text-center">
            <HelpCircle className="h-6 w-6 text-slate-400 mx-auto mb-2" />
            <div className="text-xs font-medium text-slate-700">No interview guide uploaded yet</div>
            <div className="text-[11px] text-muted-foreground mt-0.5">
              Upload a .txt, .pdf, or .md guide to automatically generate research questions.
            </div>
          </div>
        )}
      </div>

      {/* 2. Expert Transcripts Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              2. Expert Transcripts ({transcripts.length})
            </h2>
            <p className="text-xs text-muted-foreground">
              Interviews parsed into timestamped utterances and indexed into Qdrant.
              {transcripts.length > 0 && " Click transcripts to select them for targeted analysis."}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {transcripts.length > 0 && (
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={selectedTranscriptIds.size === transcripts.filter((t) => t.status === "ready").length ? deselectAllTranscripts : selectAllTranscripts}
                  className="text-[11px] font-medium text-slate-600 hover:text-slate-900 underline underline-offset-2 transition-colors"
                >
                  {selectedTranscriptIds.size === transcripts.filter((t) => t.status === "ready").length
                    ? "Deselect All"
                    : "Select All"}
                </button>
                {selectedTranscriptIds.size > 0 && (
                  <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded-full">
                    {selectedTranscriptIds.size} selected
                  </span>
                )}
              </div>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setExpertError(null);
                setExpertModalOpen(true);
              }}
              className="text-xs flex items-center gap-1.5"
            >
              <Plus className="h-3.5 w-3.5" />
              <span>Register Expert</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setTranscriptError(null);
                setTranscriptModalOpen(true);
              }}
              className="text-xs flex items-center gap-1.5"
            >
              <Upload className="h-3.5 w-3.5" />
              <span>Upload Transcript</span>
            </Button>
          </div>
        </div>

        {transcripts.length > 0 ? (
          <div className="space-y-3">
            {transcripts.map((tr) => {
              const expert = expertMap.get(tr.expert_id);
              const isReady = tr.status === "ready";
              return (
                <FileCard
                  key={tr.id}
                  type="transcript"
                  fileName={tr.file_name}
                  status={tr.status}
                  expertName={expert?.name || "Expert"}
                  market={expert?.market || undefined}
                  duration={tr.duration}
                  uploadedAt={new Date(tr.created_at).toLocaleDateString()}
                  onDelete={() => handleDeleteTranscript(tr.id)}
                  isSelected={selectedTranscriptIds.has(tr.id)}
                  onToggleSelect={isReady ? () => toggleTranscriptSelection(tr.id) : undefined}
                />
              );
            })}
          </div>
        ) : (
          <div className="rounded-xl border border-dashed border-border bg-slate-50/50 p-6 text-center">
            <Upload className="h-6 w-6 text-slate-400 mx-auto mb-2" />
            <div className="text-xs font-medium text-slate-700">No transcripts uploaded yet</div>
            <div className="text-[11px] text-muted-foreground mt-0.5">
              Register an expert and upload their interview transcript to index utterances in Qdrant.
            </div>
          </div>
        )}
      </div>

      {/* Analysis Pipeline Trigger Card */}
      <div className="rounded-xl border border-border bg-slate-50/70 p-6 space-y-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-slate-800" />
          <h3 className="text-sm font-semibold text-foreground">
            Analysis Orchestration Pipeline
          </h3>
        </div>
        <p className="text-xs text-muted-foreground leading-relaxed">
          {selectedTranscriptIds.size > 0
            ? `Analysis will run on ${selectedTranscriptIds.size} selected transcript(s). Deselect all to run across all transcripts.`
            : "Running analysis will invoke the LangGraph workflows to classify transcript evidence with Gemini LLM, synthesize grounded answers with exact timestamp provenance, compare cross-expert differences, and generate high-level strategic insights."
          }
        </p>
        <div className="pt-2 flex items-center gap-2">
          <Button
            size="sm"
            onClick={() => handleRunAnalysis()}
            disabled={analyzing || questions.length === 0 || transcripts.length === 0}
            className="flex items-center gap-1.5"
          >
            {analyzing ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin fill-current" />
                <span>Synthesizing Intelligence...</span>
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 fill-current" />
                <span>
                  {selectedTranscriptIds.size > 0
                    ? `Analyze ${selectedTranscriptIds.size} Selected`
                    : "Trigger Full Pipeline"}
                </span>
              </>
            )}
          </Button>
          {selectedTranscriptIds.size > 0 && !analyzing && (
            <button
              type="button"
              onClick={deselectAllTranscripts}
              className="text-[11px] text-slate-500 hover:text-slate-800 underline underline-offset-2 transition-colors"
            >
              Clear selection
            </button>
          )}
        </div>
      </div>

      {/* Upload Guide Modal */}
      <Modal
        isOpen={guideModalOpen}
        onClose={() => setGuideModalOpen(false)}
        title="Upload Interview Guide"
        description="Select a .txt, .pdf, or .md interview guide file to extract questions."
      >
        <form onSubmit={handleUploadGuide} className="space-y-4">
          {guideError && (
            <div className="flex items-center gap-2 p-3 rounded-md bg-rose-50 border border-rose-200 text-rose-700 text-xs">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{guideError}</span>
            </div>
          )}

          <input
            ref={guideInputRef}
            type="file"
            accept=".txt,.pdf,.md,.markdown"
            className="hidden"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                setSelectedGuideFile(e.target.files[0]);
              }
            }}
          />

          <div
            onClick={() => guideInputRef.current?.click()}
            className="border-2 border-dashed border-border rounded-lg p-8 text-center bg-slate-50/50 hover:bg-slate-50 cursor-pointer transition-colors"
          >
            <Upload className="h-8 w-8 text-slate-400 mx-auto mb-2" />
            <p className="text-xs font-medium text-slate-700">
              {selectedGuideFile ? selectedGuideFile.name : "Click to select interview guide (.txt, .pdf, .md)"}
            </p>
            <p className="text-[11px] text-muted-foreground mt-1">
              {selectedGuideFile ? `${(selectedGuideFile.size / 1024).toFixed(1)} KB` : "Up to 50MB"}
            </p>
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t border-border">
            <Button
              variant="outline"
              size="sm"
              type="button"
              disabled={guideUploading}
              onClick={() => setGuideModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              size="sm"
              type="submit"
              disabled={guideUploading || !selectedGuideFile}
              className="flex items-center gap-1.5"
            >
              {guideUploading ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Extracting Questions...</span>
                </>
              ) : (
                <span>Upload & Extract</span>
              )}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Register Expert Modal */}
      <Modal
        isOpen={expertModalOpen}
        onClose={() => setExpertModalOpen(false)}
        title="Register Expert Interviewee"
        description="Add a new expert to associate with future transcript uploads."
      >
        <form onSubmit={handleCreateExpert} className="space-y-4">
          {expertError && (
            <div className="flex items-center gap-2 p-3 rounded-md bg-rose-50 border border-rose-200 text-rose-700 text-xs">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{expertError}</span>
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-xs font-semibold">
              Expert Full Name <span className="text-rose-500">*</span>
            </label>
            <Input
              required
              disabled={expertSubmitting}
              placeholder="e.g., Dr. Emily Carter"
              value={expertName}
              onChange={(e) => setExpertName(e.target.value)}
              className="text-xs"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold">Role / Title</label>
            <Input
              disabled={expertSubmitting}
              placeholder="e.g., Consultant Urologist & Robotic Lead"
              value={expertRole}
              onChange={(e) => setExpertRole(e.target.value)}
              className="text-xs"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold">Market / Region</label>
              <Input
                disabled={expertSubmitting}
                placeholder="e.g., UK, Germany, France"
                value={expertMarket}
                onChange={(e) => setExpertMarket(e.target.value)}
                className="text-xs"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold">Organization</label>
              <Input
                disabled={expertSubmitting}
                placeholder="e.g., NHS Trust, Charité Berlin"
                value={expertOrg}
                onChange={(e) => setExpertOrg(e.target.value)}
                className="text-xs"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t border-border">
            <Button
              variant="outline"
              size="sm"
              type="button"
              disabled={expertSubmitting}
              onClick={() => setExpertModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              size="sm"
              type="submit"
              disabled={expertSubmitting}
              className="flex items-center gap-1.5"
            >
              {expertSubmitting ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Registering...</span>
                </>
              ) : (
                <span>Register Expert</span>
              )}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Upload Transcript Modal */}
      <Modal
        isOpen={transcriptModalOpen}
        onClose={() => setTranscriptModalOpen(false)}
        title="Upload Expert Transcript"
        description="Attach an interview transcript recording file to a registered expert."
      >
        <form onSubmit={handleUploadTranscript} className="space-y-4">
          {transcriptError && (
            <div className="flex items-center gap-2 p-3 rounded-md bg-rose-50 border border-rose-200 text-rose-700 text-xs">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{transcriptError}</span>
            </div>
          )}

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold">Select Expert</label>
              {experts.length === 0 && (
                <button
                  type="button"
                  onClick={() => {
                    setTranscriptModalOpen(false);
                    setExpertModalOpen(true);
                  }}
                  className="text-[11px] text-slate-700 underline font-medium"
                >
                  + Register new expert
                </button>
              )}
            </div>
            {experts.length > 0 ? (
              <Select
                value={selectedExpertId}
                onChange={(e) => setSelectedExpertId(e.target.value)}
                className="text-xs"
                disabled={transcriptUploading}
              >
                {experts.map((exp) => (
                  <option key={exp.id} value={exp.id}>
                    {exp.name} ({exp.market || "Global"}) - {exp.role || "Expert"}
                  </option>
                ))}
              </Select>
            ) : (
              <div className="text-xs text-amber-600 bg-amber-50 p-2.5 rounded border border-amber-200">
                No experts registered yet. Please register an expert first.
              </div>
            )}
          </div>

          <input
            ref={transcriptInputRef}
            type="file"
            accept=".txt,.pdf"
            className="hidden"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                setSelectedTranscriptFile(e.target.files[0]);
              }
            }}
          />

          <div
            onClick={() => transcriptInputRef.current?.click()}
            className="border-2 border-dashed border-border rounded-lg p-6 text-center bg-slate-50/50 hover:bg-slate-50 cursor-pointer transition-colors"
          >
            <Upload className="h-6 w-6 text-slate-400 mx-auto mb-2" />
            <p className="text-xs font-medium text-slate-700">
              {selectedTranscriptFile ? selectedTranscriptFile.name : "Select transcript file (.txt, .pdf)"}
            </p>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              {selectedTranscriptFile ? `${(selectedTranscriptFile.size / 1024).toFixed(1)} KB` : "Supports timestamp formats like [00:12:30]"}
            </p>
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t border-border">
            <Button
              variant="outline"
              size="sm"
              type="button"
              disabled={transcriptUploading}
              onClick={() => setTranscriptModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              size="sm"
              type="submit"
              disabled={transcriptUploading || !selectedTranscriptFile || !selectedExpertId}
              className="flex items-center gap-1.5"
            >
              {transcriptUploading ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Parsing & Indexing...</span>
                </>
              ) : (
                <span>Upload & Ingest</span>
              )}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
