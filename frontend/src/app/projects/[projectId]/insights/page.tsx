"use client";

import React, { useState, useEffect } from "react";
import { ProjectHeader } from "@/components/layout/ProjectHeader";
import { InsightCard } from "@/components/domain/InsightCard";
import { EvidenceDrawer } from "@/components/domain/EvidenceDrawer";
import { TranscriptViewer } from "@/components/domain/TranscriptViewer";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { Insight, Evidence, Transcript, Utterance } from "@/lib/types";
import { api } from "@/lib/api";
import { Lightbulb } from "lucide-react";

export default function InsightsPage({
  params,
}: {
  params: { projectId: string };
}) {
  const { projectId } = params;

  const [insights, setInsights] = useState<Insight[]>([]);
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Evidence Drawer & Transcript Viewer states
  const [selectedEvidence, setSelectedEvidence] = useState<Evidence | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [viewerOpen, setViewerOpen] = useState(false);
  const [activeUtterances, setActiveUtterances] = useState<Utterance[]>([]);
  const [activeTranscript, setActiveTranscript] = useState<Transcript | null>(null);
  const [activeExpertName, setActiveExpertName] = useState("");

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [insRes, trRes] = await Promise.allSettled([
        api.getInsights(projectId),
        api.getTranscripts(projectId),
      ]);

      if (insRes.status === "fulfilled") {
        setInsights(insRes.value.insights || []);
      }
      if (trRes.status === "fulfilled") {
        setTranscripts(trRes.value.transcripts || []);
      }
    } catch (err: any) {
      setError(err.detail || err.message || "Failed to load insights");
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
    return <LoadingState message="Loading synthesized strategic research insights..." />;
  }

  if (error) {
    return (
      <ErrorState
        title="Could not load research insights"
        message={error}
        onRetry={fetchData}
      />
    );
  }

  return (
    <div className="space-y-6 pb-12">
      <ProjectHeader
        title="Research Insights"
        description="High-level strategic takeaways synthesized across answers, differences, and grounded transcript evidence."
      />

      {insights.length === 0 ? (
        <EmptyState
          title="No strategic insights synthesized yet"
          description="Trigger the analysis pipeline in the Files section to synthesize high-level research takeaways backed by transcript evidence."
          icon={Lightbulb}
          actionLabel="Go to Files"
          onAction={() => (window.location.href = `/projects/${projectId}/files`)}
        />
      ) : (
        <div className="space-y-4">
          {insights.map((insight) => (
            <InsightCard
              key={insight.id}
              insight={insight}
              onViewEvidence={handleViewEvidence}
            />
          ))}
        </div>
      )}

      {/* Evidence Drawer */}
      <EvidenceDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        evidence={selectedEvidence}
        onOpenTranscript={handleOpenTranscript}
      />

      {/* Transcript Viewer Modal */}
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
