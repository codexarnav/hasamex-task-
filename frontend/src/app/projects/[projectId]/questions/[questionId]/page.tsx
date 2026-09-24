"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowLeft, MessageSquareText, HelpCircle } from "lucide-react";
import { AnswerCard } from "@/components/domain/AnswerCard";
import { EvidenceDrawer } from "@/components/domain/EvidenceDrawer";
import { TranscriptViewer } from "@/components/domain/TranscriptViewer";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import {
  ResearchQuestion,
  Answer,
  Expert,
  Transcript,
  Evidence,
  Utterance,
} from "@/lib/types";
import { api } from "@/lib/api";

export default function QuestionAnalysisPage({
  params,
}: {
  params: { projectId: string; questionId: string };
}) {
  const { projectId, questionId } = params;

  const [question, setQuestion] = useState<ResearchQuestion | null>(null);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [experts, setExperts] = useState<Expert[]>([]);
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedEvidence, setSelectedEvidence] = useState<Evidence | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [viewerOpen, setViewerOpen] = useState(false);
  const [activeUtterances, setActiveUtterances] = useState<Utterance[]>([]);
  const [activeTranscript, setActiveTranscript] = useState<Transcript | null>(null);
  const [activeExpertName, setActiveExpertName] = useState<string>("");

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [qListRes, qaRes, expRes, trRes] = await Promise.allSettled([
        api.getQuestions(projectId),
        api.getQuestionAnalysis(projectId, questionId),
        api.getExperts(projectId),
        api.getTranscripts(projectId),
      ]);

      if (qListRes.status === "fulfilled") {
        const found = qListRes.value.questions?.find((q) => q.id === questionId) || null;
        setQuestion(found);
      }

      if (qaRes.status === "fulfilled") {
        setAnswers(qaRes.value.answers || []);
      }

      if (expRes.status === "fulfilled") {
        setExperts(expRes.value.experts || []);
      }

      if (trRes.status === "fulfilled") {
        setTranscripts(trRes.value.transcripts || []);
      }
    } catch (err: any) {
      setError(err.detail || err.message || "Failed to load question analysis");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [projectId, questionId]);

  const handleViewEvidence = (ev: Evidence) => {
    setSelectedEvidence(ev);
    setDrawerOpen(true);
  };

  const handleOpenTranscript = async () => {
    if (!selectedEvidence?.transcript?.id) return;
    try {
      const res = await api.getTranscriptUtterances(selectedEvidence.transcript.id);
      setActiveUtterances(res.utterances || []);
      const tr = transcripts.find((t) => t.id === selectedEvidence.transcript.id) || null;
      setActiveTranscript(tr);
      setActiveExpertName(selectedEvidence.expert?.name || "Expert");
      setViewerOpen(true);
    } catch (err) {
      console.error("Failed to load utterances:", err);
    }
  };

  if (loading) {
    return <LoadingState message="Loading expert perspectives & grounded answers..." />;
  }

  if (error) {
    return (
      <ErrorState
        title="Could not load question analysis"
        message={error}
        onRetry={fetchData}
      />
    );
  }

  const expertMap: Record<string, Expert> = {};
  experts.forEach((e) => {
    expertMap[e.id] = e;
  });

  return (
    <div className="space-y-8 pb-12">
      {}
      <Link
        href={`/projects/${projectId}/questions`}
        className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        <span>Back to all questions</span>
      </Link>

      {}
      {question ? (
        <div className="rounded-xl border border-border bg-card p-6 shadow-xs space-y-3">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center justify-center rounded-md bg-slate-900 px-2.5 py-1 text-xs font-bold text-white">
              Q{question.question_number}
            </span>
            {question.category && (
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                {question.category}
              </span>
            )}
          </div>

          <h1 className="text-xl font-bold tracking-tight text-foreground leading-snug">
            {question.question_text}
          </h1>

          <div className="flex items-center gap-2 text-xs text-muted-foreground pt-1">
            <MessageSquareText className="h-3.5 w-3.5 text-slate-400" />
            <span>
              Cross-expert synthesis grounded in {answers.length} expert interview{answers.length !== 1 ? "s" : ""}
            </span>
          </div>
        </div>
      ) : (
        <div className="rounded-xl border border-border bg-card p-6 shadow-xs">
          <h1 className="text-lg font-bold text-foreground">Research Question Analysis</h1>
        </div>
      )}

      {}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold tracking-tight text-foreground">
            Expert Perspectives
          </h2>
          <span className="text-xs text-muted-foreground">
            {answers.length} synthesized perspective{answers.length !== 1 ? "s" : ""}
          </span>
        </div>

        {answers.length > 0 ? (
          <div className="space-y-4">
            {answers.map((ans) => {
              const expert = expertMap[ans.expert_id] || {
                id: ans.expert_id,
                name: "Expert",
                role: null,
                market: null,
                organization: null,
                created_at: "",
                project_id: projectId,
              };
              return (
                <AnswerCard
                  key={ans.id}
                  answer={ans}
                  expert={expert}
                  onViewEvidence={handleViewEvidence}
                />
              );
            })}
          </div>
        ) : (
          <EmptyState
            title="No grounded answers generated yet"
            description="Run the analysis pipeline in the Files section to generate evidence-backed expert answers."
            icon={HelpCircle}
            actionLabel="Go to Files"
            onAction={() => (window.location.href = `/projects/${projectId}/files`)}
          />
        )}
      </div>

      {}
      <EvidenceDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        evidence={selectedEvidence}
        onOpenTranscript={handleOpenTranscript}
      />

      {}
      {activeTranscript && (
        <TranscriptViewer
          isOpen={viewerOpen}
          onClose={() => setViewerOpen(false)}
          transcript={activeTranscript}
          expertName={activeExpertName}
          utterances={activeUtterances}
          highlightedUtteranceId={selectedEvidence?.utterance_id}
        />
      )}
    </div>
  );
}
