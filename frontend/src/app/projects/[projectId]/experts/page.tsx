"use client";

import React, { useState, useEffect } from "react";
import { ProjectHeader } from "@/components/layout/ProjectHeader";
import { ExpertCard } from "@/components/domain/ExpertCard";
import { TranscriptViewer } from "@/components/domain/TranscriptViewer";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { Expert, Transcript, Utterance } from "@/lib/types";
import { api } from "@/lib/api";
import { Users } from "lucide-react";

export default function ExpertsPage({
  params,
}: {
  params: { projectId: string };
}) {
  const { projectId } = params;

  const [experts, setExperts] = useState<Expert[]>([]);
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [viewerOpen, setViewerOpen] = useState(false);
  const [selectedTranscript, setSelectedTranscript] = useState<Transcript | null>(null);
  const [selectedExpertName, setSelectedExpertName] = useState("");
  const [utterances, setUtterances] = useState<Utterance[]>([]);
  const [loadingUtterances, setLoadingUtterances] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [expRes, trRes] = await Promise.allSettled([
        api.getExperts(projectId),
        api.getTranscripts(projectId),
      ]);

      if (expRes.status === "fulfilled") {
        setExperts(expRes.value.experts || []);
      }
      if (trRes.status === "fulfilled") {
        setTranscripts(trRes.value.transcripts || []);
      }
    } catch (err: any) {
      setError(err.detail || err.message || "Failed to load experts");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [projectId]);

  const handleOpenTranscript = async (expert: Expert, transcript?: Transcript) => {
    if (!transcript) return;
    try {
      setLoadingUtterances(true);
      setSelectedTranscript(transcript);
      setSelectedExpertName(expert.name);
      const res = await api.getTranscriptUtterances(transcript.id);
      setUtterances(res.utterances || []);
      setViewerOpen(true);
    } catch (err) {
      console.error("Failed to load transcript utterances:", err);
    } finally {
      setLoadingUtterances(false);
    }
  };

  if (loading) {
    return <LoadingState message="Loading registered experts and transcripts..." />;
  }

  if (error) {
    return (
      <ErrorState
        title="Could not load experts"
        message={error}
        onRetry={fetchData}
      />
    );
  }

  const transcriptByExpertId = new Map(transcripts.map((t) => [t.expert_id, t]));

  return (
    <div className="space-y-6 pb-12">
      <ProjectHeader
        title="Expert Interviewees"
        description="Healthcare professionals, surgical leads, and hospital procurement directors interviewed for this study."
      />

      {experts.length === 0 ? (
        <EmptyState
          title="No expert interviewees registered yet"
          description="Register experts and upload their interview transcripts in the Files section to index their perspectives."
          icon={Users}
          actionLabel="Go to Files & Register Expert"
          onAction={() => (window.location.href = `/projects/${projectId}/files`)}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {experts.map((exp) => {
            const tr = transcriptByExpertId.get(exp.id);
            return (
              <div
                key={exp.id}
                onClick={() => tr && handleOpenTranscript(exp, tr)}
                className={tr ? "cursor-pointer" : "opacity-90"}
              >
                <ExpertCard expert={exp} transcript={tr} />
              </div>
            );
          })}
        </div>
      )}

      {selectedTranscript && (
        <TranscriptViewer
          isOpen={viewerOpen}
          onClose={() => setViewerOpen(false)}
          transcript={selectedTranscript}
          expertName={selectedExpertName}
          utterances={utterances}
        />
      )}
    </div>
  );
}
