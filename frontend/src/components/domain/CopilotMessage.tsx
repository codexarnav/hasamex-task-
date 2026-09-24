"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { CopilotMessage as CopilotMessageType, Evidence } from "@/lib/types";
import { SourceCard } from "./SourceCard";
import { User, Sparkles, AlertCircle } from "lucide-react";

interface CopilotMessageProps {
  message: CopilotMessageType;
  onViewEvidence: (evidence: Evidence) => void;
}

export function CopilotMessage({ message, onViewEvidence }: CopilotMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-3 text-sm",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-lg bg-slate-900 text-white font-semibold text-xs shadow-xs mt-0.5">
          <Sparkles className="h-4 w-4" />
        </div>
      )}

      <div
        className={cn(
          "rounded-xl p-4 max-w-2xl space-y-3",
          isUser
            ? "bg-slate-900 text-white"
            : "border border-border bg-card shadow-xs text-slate-800"
        )}
      >
        <div className="leading-relaxed whitespace-pre-wrap">{message.content}</div>

        {message.insufficient_evidence && (
          <div className="flex items-center gap-1.5 text-xs text-amber-700 bg-amber-50 p-2.5 rounded border border-amber-200">
            <AlertCircle className="h-4 w-4 shrink-0 text-amber-600" />
            <span>The available transcripts contained insufficient evidence to answer completely.</span>
          </div>
        )}

        {!isUser && message.evidence && message.evidence.length > 0 && (
          <div className="pt-3 border-t border-border/60 space-y-2">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Transcript Citations ({message.evidence.length})
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              {message.evidence.map((ev, idx) => (
                <SourceCard
                  key={ev.id || idx}
                  evidence={ev}
                  onClick={() => onViewEvidence(ev)}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-lg bg-slate-200 text-slate-700 font-semibold text-xs mt-0.5">
          <User className="h-4 w-4" />
        </div>
      )}
    </div>
  );
}
