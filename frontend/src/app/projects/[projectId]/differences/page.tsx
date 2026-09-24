"use client";

import React, { useState, useEffect } from "react";
import { ProjectHeader } from "@/components/layout/ProjectHeader";
import { DifferenceCard } from "@/components/domain/DifferenceCard";
import { EvidenceDrawer } from "@/components/domain/EvidenceDrawer";
import { TranscriptViewer } from "@/components/domain/TranscriptViewer";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { Evidence, Difference, Transcript, Utterance } from "@/lib/types";
import { api } from "@/lib/api";
import { GitCompare } from "lucide-react";

export default function DifferencesPage({
  params,
}: {
  params: { projectId: string };
}) {
  const { projectId } = params;

  const [differences, setDifferences] = useState<Difference[]>([]);
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

      const [diffRes, trRes] = await Promise.allSettled([
        api.getDifferences(projectId),
        api.getTranscripts(projectId),
      ]);

      if (diffRes.status === "fulfilled") {
        setDifferences(diffRes.value.differences || []);
      }
      if (trRes.status === "fulfilled") {
        setTranscripts(trRes.value.transcripts || []);
      }
    } catch (err: any) {
      setError(err.detail || err.message || "Failed to load differences");
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
    return <LoadingState message="Loading cross-expert differences & contrasts..." />;
  }

  if (error) {
    return (
      <ErrorState
        title="Could not load differences"
        message={error}
        onRetry={fetchData}
      />
    );
  }

  return (
    <div className="space-y-6 pb-12">
      <ProjectHeader
        title="Cross-Expert Differences"
        description="Contrasting clinical viewpoints, regional procurement models, and regulatory divergences identified across interviewed experts."
      />

      {differences.length === 0 ? (
        <EmptyState
          title="No cross-expert differences detected yet"
          description="Upload transcripts for multiple experts and trigger the analysis pipeline to detect comparative divergences."
          icon={GitCompare}
          actionLabel="Go to Files"
          onAction={() => (window.location.href = `/projects/${projectId}/files`)}
        />
      ) : (
        <div className="space-y-6">
          {differences.map((diff) => (
            <DifferenceCard
              key={diff.id}
              difference={diff}
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
