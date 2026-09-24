"use client";

import React from "react";
import { Difference, Evidence } from "@/lib/types";
import { Button } from "../ui/Button";
import { GitCompare, Quote, CheckCircle2 } from "lucide-react";

interface DifferenceCardProps {
  difference: Difference;
  onViewEvidence: (evidence: Evidence) => void;
}

export function DifferenceCard({ difference, onViewEvidence }: DifferenceCardProps) {
  const isNoDifference =
    !difference.title ||
    difference.title.toLowerCase().includes("no significant difference") ||
    difference.perspectives.length === 0;

  if (isNoDifference) {
    return (
      <div className="rounded-xl border border-border bg-card p-6 shadow-xs space-y-3">
        <div className="flex items-center gap-2 text-slate-700">
          <CheckCircle2 className="h-4 w-4 text-emerald-600" />
          <h3 className="text-base font-semibold text-foreground">
            No Significant Difference Detected
          </h3>
        </div>
        <p className="text-sm text-muted-foreground leading-relaxed">
          {difference.description ||
            "The available expert perspectives are broadly aligned for this research question."}
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-xs space-y-5">
      {/* Title & Description */}
      <div className="space-y-1.5 pb-3 border-b border-border">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          <GitCompare className="h-3.5 w-3.5 text-slate-500" />
          <span>Cross-Expert Divergence</span>
        </div>
        <h3 className="text-base font-semibold text-foreground">{difference.title}</h3>
        {difference.description && (
          <p className="text-sm text-muted-foreground leading-relaxed">{difference.description}</p>
        )}
      </div>

      {/* Per-Expert Perspectives Grid/Stack */}
      <div className="space-y-3">
        <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Contrasting Perspectives
        </div>
        <div className="grid gap-3 sm:grid-cols-3">
          {difference.perspectives.map((p, idx) => (
            <div
              key={p.expert_id || idx}
              className="rounded-lg border border-border bg-slate-50/70 p-3.5 space-y-1.5"
            >
              <div className="text-xs font-bold text-foreground truncate">
                {p.expert_name}
              </div>
              <p className="text-xs leading-relaxed text-slate-700 font-serif italic">
                &ldquo;{p.perspective}&rdquo;
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Supporting Evidence Bar */}
      {difference.evidence.length > 0 && (
        <div className="pt-2 border-t border-border/60">
          <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
            Supporting Evidence ({difference.evidence.length})
          </div>
          <div className="flex flex-wrap gap-2">
            {difference.evidence.map((ev, idx) => (
              <Button
                key={ev.id || idx}
                variant="outline"
                size="sm"
                onClick={() => onViewEvidence(ev)}
                className="text-xs font-medium h-7 bg-white hover:bg-slate-50 flex items-center gap-1.5 border-slate-200 text-slate-700"
              >
                <Quote className="h-3 w-3 text-slate-400" />
                <span>{ev.expert.name.split(" ")[0]} Quote</span>
                {ev.timestamp.start && (
                  <span className="font-mono text-[10px] text-slate-400">
                    [{ev.timestamp.start}]
                  </span>
                )}
              </Button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
