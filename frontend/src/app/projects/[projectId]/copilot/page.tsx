"use client";

import React, { useState, useEffect, useRef } from "react";
import { CopilotMessage } from "@/components/domain/CopilotMessage";
import { EvidenceDrawer } from "@/components/domain/EvidenceDrawer";
import { TranscriptViewer } from "@/components/domain/TranscriptViewer";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import {
  CopilotMessage as CopilotMessageType,
  Evidence,
  Transcript,
  Utterance,
} from "@/lib/types";
import { api } from "@/lib/api";
import { Send, Sparkles, HelpCircle, Loader2, AlertCircle } from "lucide-react";

export default function CopilotPage({
  params,
}: {
  params: { projectId: string };
}) {
  const { projectId } = params;

  const [messages, setMessages] = useState<CopilotMessageType[]>([]);
  const [inputQuery, setInputQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedEvidence, setSelectedEvidence] = useState<Evidence | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [viewerOpen, setViewerOpen] = useState(false);
  const [activeUtterances, setActiveUtterances] = useState<Utterance[]>([]);
  const [activeTranscript, setActiveTranscript] = useState<Transcript | null>(null);
  const [activeExpertName, setActiveExpertName] = useState("");
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.getTranscripts(projectId)
      .then((res) => setTranscripts(res.transcripts || []))
      .catch(() => {});
  }, [projectId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const samplePrompts = [
    "What are the biggest clinical workflow bottlenecks during initial deployment?",
    "How do regional reimbursement and statutory insurance models influence hospital purchasing?",
    "What did the UK expert say about NHS Trust capital purchasing?",
    "What are the primary cross-market differences between UK, Germany, and France?",
  ];

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    const query = inputQuery.trim();
    if (!query || loading) return;

    const userMsg: CopilotMessageType = {
      id: `user-${Date.now()}`,
      role: "user",
      content: query,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery("");
    setError(null);
    setLoading(true);

    try {
      const response = await api.askCopilot(projectId, query);
      const assistantMsg: CopilotMessageType = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: response.answer,
        evidence: response.evidence || [],
        insufficient_evidence: response.insufficient_evidence,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setError(err.detail || err.message || "Failed to query Copilot");
      const errorMsg: CopilotMessageType = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: "Sorry, I encountered an error while synthesizing qualitative evidence for your question.",
        insufficient_evidence: true,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSamplePrompt = (prompt: string) => {
    setInputQuery(prompt);
  };

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

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] max-h-[850px] space-y-4">
      {}
      <div className="pb-3 border-b border-border shrink-0">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded bg-slate-900 text-white">
            <Sparkles className="h-3.5 w-3.5" />
          </div>
          <h1 className="text-lg font-bold tracking-tight text-foreground">
            Research Copilot
          </h1>
        </div>
        <p className="text-xs text-muted-foreground mt-0.5">
          Ask arbitrary qualitative inquiries across all interview transcripts. Answers are synthesized strictly from grounded quotes.
        </p>
      </div>

      {}
      <div className="flex-1 overflow-y-auto pr-1 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-8">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-600 mb-4">
              <Sparkles className="h-6 w-6" />
            </div>
            <h3 className="text-sm font-semibold text-foreground">
              Interrogate Your Qualitative Research
            </h3>
            <p className="mt-1 text-xs text-muted-foreground max-w-sm">
              The Copilot retrieves relevant transcript utterances from Qdrant and synthesizes grounded answers with exact source citations.
            </p>

            <div className="mt-6 w-full max-w-md space-y-2">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                Suggested inquiries:
              </div>
              <div className="grid gap-2">
                {samplePrompts.map((p, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSelectSamplePrompt(p)}
                    className="text-left text-xs p-2.5 rounded-lg border border-border bg-card hover:bg-slate-50 transition-colors text-slate-700"
                  >
                    &ldquo;{p}&rdquo;
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <CopilotMessage
                key={msg.id}
                message={msg}
                onViewEvidence={handleViewEvidence}
              />
            ))}
            {loading && (
              <div className="flex items-center gap-2 p-4 rounded-xl bg-slate-50 border border-border text-xs text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin text-slate-700" />
                <span>Searching Qdrant utterances and synthesizing grounded response...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {}
      {messages.length > 0 && (
        <div className="flex items-center gap-2 overflow-x-auto py-1 shrink-0 scrollbar-none">
          <span className="text-[11px] text-muted-foreground whitespace-nowrap font-medium flex items-center gap-1">
            <HelpCircle className="h-3 w-3" /> Try:
          </span>
          {samplePrompts.slice(0, 2).map((p, idx) => (
            <button
              key={idx}
              type="button"
              disabled={loading}
              onClick={() => handleSelectSamplePrompt(p)}
              className="whitespace-nowrap text-[11px] px-2.5 py-1 rounded-full border border-border bg-card text-slate-600 hover:bg-slate-50 transition-colors"
            >
              {p}
            </button>
          ))}
        </div>
      )}

      {}
      <form onSubmit={handleSend} className="flex items-center gap-2 shrink-0 pt-2 border-t border-border">
        <Input
          placeholder="Ask any question about your interview transcripts..."
          value={inputQuery}
          disabled={loading}
          onChange={(e) => setInputQuery(e.target.value)}
          className="text-xs h-10 shadow-xs"
        />
        <Button
          type="submit"
          size="sm"
          disabled={loading || !inputQuery.trim()}
          className="h-10 px-4 flex items-center gap-1.5 shrink-0 shadow-sm"
        >
          {loading ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Send className="h-3.5 w-3.5" />
          )}
          <span>Ask</span>
        </Button>
      </form>

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
