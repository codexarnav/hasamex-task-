"use client";

import React from "react";
import { Evidence } from "@/lib/types";
import { Clock, Globe, Quote } from "lucide-react";

interface SourceCardProps {
  evidence: Evidence;
  onClick: () => void;
}

export function SourceCard({ evidence, onClick }: SourceCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="text-left w-full rounded-lg border border-border bg-white p-3 shadow-2xs transition-all hover:border-slate-300 hover:bg-slate-50/50 space-y-1.5"
    >
      <div className="flex items-center justify-between text-[11px] font-medium text-muted-foreground">
        <span className="flex items-center gap-1 text-slate-900 font-semibold">
          <Globe className="h-3 w-3 text-slate-400" />
          {evidence.expert.name} ({evidence.expert.market || "Global"})
        </span>
        {evidence.timestamp.start && (
          <span className="flex items-center gap-1 font-mono text-[10px] text-slate-400">
            <Clock className="h-2.5 w-2.5" />
            {evidence.timestamp.start}
          </span>
        )}
      </div>
      <p className="text-xs font-serif italic text-slate-700 line-clamp-2">
        &ldquo;{evidence.quote}&rdquo;
      </p>
    </button>
  );
}
