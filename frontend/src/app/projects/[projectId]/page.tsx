"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ProjectHeader } from "@/components/layout/ProjectHeader";
import { StatCard } from "@/components/ui/StatCard";
import { InsightCard } from "@/components/domain/InsightCard";
import { EvidenceDrawer } from "@/components/domain/EvidenceDrawer";
import { TranscriptViewer } from "@/components/domain/TranscriptViewer";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import {
  Project,
  ResearchQuestion,
  Expert,
  Transcript,
  Evidence,
  Difference,
  Insight,
  Utterance,
} from "@/lib/types";
import { api } from "@/lib/api";
import {
  ArrowRight,
  HelpCircle,
  Users,
  Quote,
  GitCompare,
  Lightbulb,
  Sparkles,
  FolderOpen,
} from "lucide-react";

export default function ProjectOverviewPage({
  params,
}: {
  params: { projectId: string };
}) {
  const { projectId } = params;

  const [project, setProject] = useState<Project | null>(null);
  const [questions, setQuestions] = useState<ResearchQuestion[]>([]);
  const [experts, setExperts] = useState<Expert[]>([]);
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [evidenceList, setEvidenceList] = useState<Evidence[]>([]);
  const [differences, setDifferences] = useState<Difference[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [totalAnswers, setTotalAnswers] = useState<number>(0);

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

      const [
        projRes,
        qRes,
        expRes,
        trRes,
        evRes,
        diffRes,
        insRes,
        analysisRes,
      ] = await Promise.allSettled([
        api.getProject(projectId),
        api.getQuestions(projectId),
        api.getExperts(projectId),
        api.getTranscripts(projectId),
        api.getEvidenceList(projectId),
        api.getDifferences(projectId),
        api.getInsights(projectId),
        api.getAnalysis(projectId),
      ]);

      if (projRes.status === "fulfilled") setProject(projRes.value);
      if (qRes.status === "fulfilled") setQuestions(qRes.value.questions || []);
      if (expRes.status === "fulfilled") setExperts(expRes.value.experts || []);
      if (trRes.status === "fulfilled") setTranscripts(trRes.value.transcripts || []);
      if (evRes.status === "fulfilled") setEvidenceList(evRes.value.evidence || []);
      if (diffRes.status === "fulfilled") setDifferences(diffRes.value.differences || []);
      if (insRes.status === "fulfilled") setInsights(insRes.value.insights || []);

      if (analysisRes.status === "fulfilled" && analysisRes.value.questions) {
        let count = 0;
        analysisRes.value.questions.forEach((q) => {
          count += q.answers?.length || 0;
        });
        setTotalAnswers(count);
      }
    } catch (err: any) {
      setError(err.detail || err.message || "Failed to load project overview");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [projectId]);

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
    return <LoadingState message="Loading research project overview..." />;
  }

  if (error || !project) {
    return (
      <ErrorState
        title="Could not load project overview"
        message={error || "Project not found"}
        onRetry={fetchData}
      />
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {}
      <ProjectHeader
        title={project.name}
        description={project.objective || "Qualitative intelligence and grounded transcript analysis"}
        status={project.status}
        actions={
          <Link href={`/projects/${projectId}/copilot`}>
            <Button size="sm" className="shadow-sm flex items-center gap-1.5">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Open Copilot</span>
            </Button>
          </Link>
        }
      />

      {}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          label="Interviewed Experts"
          value={String(experts.length)}
          description={`${transcripts.length} transcripts indexed in vector store`}
        />
        <StatCard
          label="Extracted Questions"
          value={String(questions.length)}
          description="Dynamically extracted from interview guide"
        />
        <StatCard
          label="Grounded Analyses"
          value={String(totalAnswers)}
          description={`${evidenceList.length} supporting quotes with timestamp provenance`}
        />
      </div>

      {}
      <div className="rounded-xl border border-border bg-card p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-border">
          <div>
            <h2 className="text-base font-semibold text-foreground">
              Research Pipeline Status
            </h2>
            <p className="text-xs text-muted-foreground">
              End-to-end evidence classification and qualitative synthesis breakdown
            </p>
          </div>
          <Link
            href={`/projects/${projectId}/questions`}
            className="text-xs font-medium text-slate-900 hover:underline flex items-center gap-1"
          >
            <span>View all questions</span>
            <ArrowRight className="h-3 w-3" />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-2">
          <Link
            href={`/projects/${projectId}/questions`}
            className="rounded-lg border border-border p-3.5 hover:bg-slate-50 transition-colors"
          >
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
              <HelpCircle className="h-3.5 w-3.5 text-slate-400" />
              <span>Questions</span>
            </div>
            <div className="text-lg font-bold text-foreground">{questions.length}</div>
            <div className="text-[11px] text-emerald-600 font-medium">
              {questions.length > 0 ? "Extracted" : "Pending Guide"}
            </div>
          </Link>

          <Link
            href={`/projects/${projectId}/experts`}
            className="rounded-lg border border-border p-3.5 hover:bg-slate-50 transition-colors"
          >
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
              <Users className="h-3.5 w-3.5 text-slate-400" />
              <span>Experts</span>
            </div>
            <div className="text-lg font-bold text-foreground">{experts.length}</div>
            <div className="text-[11px] text-emerald-600 font-medium">
              {transcripts.length} Transcripts
            </div>
          </Link>

          <Link
            href={`/projects/${projectId}/evidence`}
            className="rounded-lg border border-border p-3.5 hover:bg-slate-50 transition-colors"
          >
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
              <Quote className="h-3.5 w-3.5 text-slate-400" />
              <span>Evidence</span>
            </div>
            <div className="text-lg font-bold text-foreground">{evidenceList.length} Quotes</div>
            <div className="text-[11px] text-slate-500">Timestamped</div>
          </Link>

          <Link
            href={`/projects/${projectId}/differences`}
            className="rounded-lg border border-border p-3.5 hover:bg-slate-50 transition-colors"
          >
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
              <GitCompare className="h-3.5 w-3.5 text-slate-400" />
              <span>Differences</span>
            </div>
            <div className="text-lg font-bold text-foreground">{differences.length} Detected</div>
            <div className="text-[11px] text-slate-500">Cross-market</div>
          </Link>

          <Link
            href={`/projects/${projectId}/insights`}
            className="rounded-lg border border-border p-3.5 hover:bg-slate-50 transition-colors"
          >
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
              <Lightbulb className="h-3.5 w-3.5 text-slate-400" />
              <span>Insights</span>
            </div>
            <div className="text-lg font-bold text-foreground">{insights.length} Strategic</div>
            <div className="text-[11px] text-slate-500">Synthesized</div>
          </Link>
        </div>
      </div>

      {}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold tracking-tight text-foreground">
              Research Highlights & Insights
            </h2>
            <p className="text-xs text-muted-foreground">
              Synthesized qualitative findings backed by transcript evidence
            </p>
          </div>
          {insights.length > 0 && (
            <Link
              href={`/projects/${projectId}/insights`}
              className="text-xs font-medium text-slate-900 hover:underline flex items-center gap-1"
            >
              <span>Explore all insights</span>
              <ArrowRight className="h-3 w-3" />
            </Link>
          )}
        </div>

        {insights.length > 0 ? (
          <div className="space-y-4">
            {insights.slice(0, 3).map((insight) => (
              <InsightCard
                key={insight.id}
                insight={insight}
                onViewEvidence={handleViewEvidence}
              />
            ))}
          </div>
        ) : (
          <EmptyState
            title="No insights synthesized yet"
            description="Upload your interview guide and expert transcripts, then trigger the analysis pipeline to generate grounded research insights."
            icon={FolderOpen}
            actionLabel="Manage Files & Run Analysis"
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
