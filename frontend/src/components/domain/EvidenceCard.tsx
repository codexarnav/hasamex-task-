"use client";

import React from "react";
import { Evidence } from "@/lib/types";
import { Button } from "../ui/Button";
import { Clock, User, Globe, ArrowRight } from "lucide-react";

interface EvidenceCardProps {
  evidence: Evidence;
  onView: (evidence: Evidence) => void;
}

export function EvidenceCard({ evidence, onView }: EvidenceCardProps) {
  const timestampStr = evidence.timestamp.start
    ? `${evidence.timestamp.start}${evidence.timestamp.end ? ` - ${evidence.timestamp.end}` : ""}`
    : "No timestamp";

  return (
    <div className="group rounded-xl border border-border bg-card p-5 shadow-xs transition-all hover:border-slate-300 space-y-3">
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-2 font-medium text-foreground">
          <User className="h-3.5 w-3.5 text-slate-400" />
          <span>{evidence.expert.name}</span>
          {evidence.expert.market && (
            <span className="inline-flex items-center gap-1 rounded bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600">
              <Globe className="h-2.5 w-2.5 text-slate-400" />
              {evidence.expert.market}
            </span>
          )}
        </div>

        <div className="flex items-center gap-1 font-mono text-[11px] text-muted-foreground">
          <Clock className="h-3 w-3 text-slate-400" />
          <span>{timestampStr}</span>
        </div>
      </div>

      <blockquote className="text-sm font-serif italic leading-relaxed text-slate-800 line-clamp-3">
        &ldquo;{evidence.quote}&rdquo;
      </blockquote>

      <div className="flex items-center justify-between pt-2 border-t border-border/60 text-xs">
        <span className="text-muted-foreground truncate max-w-[280px]">
          {evidence.topic || evidence.transcript.file_name}
        </span>

        <Button
          variant="ghost"
          size="sm"
          onClick={() => onView(evidence)}
          className="h-7 text-xs font-medium text-slate-900 hover:bg-slate-100 flex items-center gap-1 px-2.5"
        >
          <span>Inspect</span>
          <ArrowRight className="h-3 w-3 text-slate-500 group-hover:translate-x-0.5 transition-transform" />
        </Button>
      </div>
    </div>
  );
}
