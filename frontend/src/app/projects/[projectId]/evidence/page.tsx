"use client";

import React, { useState, useEffect, useMemo } from "react";
import { ProjectHeader } from "@/components/layout/ProjectHeader";
import { EvidenceCard } from "@/components/domain/EvidenceCard";
import { EvidenceDrawer } from "@/components/domain/EvidenceDrawer";
import { TranscriptViewer } from "@/components/domain/TranscriptViewer";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { Evidence, Expert, Transcript, Utterance } from "@/lib/types";
import { api } from "@/lib/api";
import { Search, Quote } from "lucide-react";

export default function EvidenceExplorerPage({
  params,
}: {
  params: { projectId: string };
}) {
  const { projectId } = params;

  const [evidenceList, setEvidenceList] = useState<Evidence[]>([]);
  const [experts, setExperts] = useState<Expert[]>([]);
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedExpert, setSelectedExpert] = useState("all");
  const [selectedMarket, setSelectedMarket] = useState("all");

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

      const [evRes, expRes, trRes] = await Promise.allSettled([
        api.getEvidenceList(projectId),
        api.getExperts(projectId),
        api.getTranscripts(projectId),
      ]);

      if (evRes.status === "fulfilled") {
        setEvidenceList(evRes.value.evidence || []);
      }
      if (expRes.status === "fulfilled") {
        setExperts(expRes.value.experts || []);
      }
      if (trRes.status === "fulfilled") {
        setTranscripts(trRes.value.transcripts || []);
      }
    } catch (err: any) {
      setError(err.detail || err.message || "Failed to load evidence items");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [projectId]);

  const distinctMarkets = useMemo(() => {
    const set = new Set<string>();
    experts.forEach((e) => {
      if (e.market) set.add(e.market);
    });
    return Array.from(set);
  }, [experts]);

  const filteredEvidence = useMemo(() => {
    return evidenceList.filter((ev) => {
      const q = searchQuery.toLowerCase();
      const matchesSearch =
        !searchQuery ||
        ev.quote.toLowerCase().includes(q) ||
        (ev.topic && ev.topic.toLowerCase().includes(q)) ||
        (ev.expert?.name && ev.expert.name.toLowerCase().includes(q));

      const matchesExpert =
        selectedExpert === "all" || ev.expert?.id === selectedExpert;

      const matchesMarket =
        selectedMarket === "all" || ev.expert?.market === selectedMarket;

      return matchesSearch && matchesExpert && matchesMarket;
    });
  }, [evidenceList, searchQuery, selectedExpert, selectedMarket]);

  const handleView = (ev: Evidence) => {
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
    return <LoadingState message="Loading grounded evidence records..." />;
  }

  if (error) {
    return (
      <ErrorState
        title="Could not load evidence records"
        message={error}
        onRetry={fetchData}
      />
    );
  }

  return (
    <div className="space-y-6 pb-12">
      <ProjectHeader
        title="Evidence Explorer"
        description="All grounded qualitative evidence segments extracted from transcript utterances with exact timestamp provenance."
      />

      {/* Search & Filter Toolbar */}
      <div className="flex flex-col sm:flex-row items-center gap-3 bg-card p-4 rounded-xl border border-border shadow-2xs">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search quotes, topics, or claims..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 text-xs"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Select
            value={selectedExpert}
            onChange={(e) => setSelectedExpert(e.target.value)}
            className="text-xs h-9 w-full sm:w-44"
          >
            <option value="all">All Experts ({experts.length})</option>
            {experts.map((exp) => (
              <option key={exp.id} value={exp.id}>
                {exp.name} ({exp.market || "Global"})
              </option>
            ))}
          </Select>

          <Select
            value={selectedMarket}
            onChange={(e) => setSelectedMarket(e.target.value)}
            className="text-xs h-9 w-full sm:w-36"
          >
            <option value="all">All Markets</option>
            {distinctMarkets.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </Select>
        </div>
      </div>

      {/* Evidence Cards Grid */}
      {filteredEvidence.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {filteredEvidence.map((ev) => (
            <EvidenceCard key={ev.id} evidence={ev} onView={handleView} />
          ))}
        </div>
      ) : evidenceList.length === 0 ? (
        <EmptyState
          title="No evidence records extracted yet"
          description="Trigger the research analysis pipeline in the Files section to classify transcript utterances and extract validated evidence."
          icon={Quote}
          actionLabel="Go to Files"
          onAction={() => (window.location.href = `/projects/${projectId}/files`)}
        />
      ) : (
        <EmptyState
          title="No evidence matched your filter"
          description="Try clearing your search query or adjusting market and expert filters."
          icon={Quote}
          actionLabel="Clear filters"
          onAction={() => {
            setSearchQuery("");
            setSelectedExpert("all");
            setSelectedMarket("all");
          }}
        />
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
