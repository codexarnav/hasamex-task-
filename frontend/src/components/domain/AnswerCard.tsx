"use client";

import React from "react";
import { Answer, Expert, Evidence } from "@/lib/types";
import { Button } from "../ui/Button";
import { Globe, Quote, CheckCircle2 } from "lucide-react";

interface AnswerCardProps {
  answer: Answer;
  expert?: Expert;
  onViewEvidence: (evidence: Evidence) => void;
}

export function AnswerCard({ answer, expert, onViewEvidence }: AnswerCardProps) {
  const expertName = expert?.name || "Expert";
  const expertRole = expert?.role || "Specialist";
  const expertMarket = expert?.market || "Global";

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-xs space-y-4">
      {/* Header: Expert & Market */}
      <div className="flex items-start justify-between gap-4 pb-3 border-b border-border">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Perspective
            </span>
            <span className="text-muted-foreground">·</span>
            <span className="inline-flex items-center gap-1 text-xs font-semibold text-slate-800">
              <Globe className="h-3 w-3 text-slate-400" />
              {expertMarket}
            </span>
          </div>
          <h3 className="text-base font-semibold text-foreground mt-0.5">{expertName}</h3>
          <p className="text-xs text-muted-foreground">{expertRole}</p>
        </div>

        <div className="flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
          <CheckCircle2 className="h-3 w-3" />
          <span>Grounded</span>
        </div>
      </div>

      {/* Synthesized Answer Body */}
      <div>
        <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
          Synthesized Answer
        </div>
        <p className="text-sm leading-relaxed text-slate-800">{answer.answer_text}</p>
      </div>

      {/* Supporting Evidence Bar */}
      <div className="pt-2">
        <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2 flex items-center justify-between">
          <span>Supporting Evidence ({answer.evidence.length})</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {answer.evidence.map((ev, idx) => (
            <Button
              key={ev.id || idx}
              variant="outline"
              size="sm"
              onClick={() => onViewEvidence(ev)}
              className="text-xs font-medium h-8 bg-slate-50 hover:bg-slate-100 flex items-center gap-1.5 border-slate-200 text-slate-700"
            >
              <Quote className="h-3 w-3 text-slate-400" />
              <span>Evidence #{idx + 1}</span>
              {ev.timestamp.start && (
                <span className="font-mono text-[10px] text-slate-400">
                  [{ev.timestamp.start}]
                </span>
              )}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}
