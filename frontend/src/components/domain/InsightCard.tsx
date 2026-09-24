"use client";

import React from "react";
import { Insight, Evidence } from "@/lib/types";
import { Button } from "../ui/Button";
import { Lightbulb, Quote, Sparkles } from "lucide-react";

interface InsightCardProps {
  insight: Insight;
  onViewEvidence: (evidence: Evidence) => void;
}

export function InsightCard({ insight, onViewEvidence }: InsightCardProps) {
  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-xs space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1.5 flex-1">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 rounded bg-slate-900 text-white px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider">
              <Lightbulb className="h-3 w-3" />
              Insight
            </span>
            {insight.confidence !== null && (
              <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                <Sparkles className="h-3 w-3" />
                <span>Confidence {(insight.confidence * 100).toFixed(0)}%</span>
              </span>
            )}
          </div>
          <h3 className="text-base font-semibold text-foreground leading-snug">
            {insight.title}
          </h3>
        </div>
      </div>

      <p className="text-sm leading-relaxed text-slate-700">{insight.summary}</p>

      {insight.evidence.length > 0 && (
        <div className="pt-3 border-t border-border/60">
          <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
            Grounding Evidence ({insight.evidence.length})
          </div>
          <div className="flex flex-wrap gap-2">
            {insight.evidence.map((ev, idx) => (
              <Button
                key={ev.id || idx}
                variant="outline"
                size="sm"
                onClick={() => onViewEvidence(ev)}
                className="text-xs font-medium h-7 bg-slate-50 hover:bg-slate-100 flex items-center gap-1.5 border-slate-200 text-slate-700"
              >
                <Quote className="h-3 w-3 text-slate-400" />
                <span>
                  {ev.expert.name.split(" ")[0]} ({ev.expert.market || "Global"})
                </span>
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
