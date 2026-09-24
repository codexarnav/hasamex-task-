import React from "react";
import Link from "next/link";
import { ResearchQuestion } from "@/lib/types";
import { ArrowRight, MessageSquareText } from "lucide-react";

interface QuestionCardProps {
  question: ResearchQuestion;
  projectId: string;
  perspectiveCount?: number;
}

export function QuestionCard({
  question,
  projectId,
  perspectiveCount = 3,
}: QuestionCardProps) {
  return (
    <div className="group rounded-xl border border-border bg-card p-5 shadow-xs transition-all hover:border-slate-300 hover:shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-2 flex-1">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center justify-center rounded-md bg-slate-900 px-2 py-0.5 text-[11px] font-bold text-white tracking-wide">
              Q{question.question_number}
            </span>
            {question.category && (
              <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                {question.category}
              </span>
            )}
          </div>

          <h3 className="text-base font-semibold text-foreground group-hover:text-slate-900 transition-colors leading-snug">
            {question.question_text}
          </h3>

          <div className="flex items-center gap-1.5 text-xs text-muted-foreground pt-1">
            <MessageSquareText className="h-3.5 w-3.5 text-slate-400" />
            <span>{perspectiveCount} expert perspectives analyzed</span>
          </div>
        </div>

        <Link
          href={`/projects/${projectId}/questions/${question.id}`}
          className="inline-flex items-center gap-1 text-xs font-medium text-slate-900 bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-md transition-colors shrink-0"
        >
          <span>Analysis</span>
          <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
        </Link>
      </div>
    </div>
  );
}
