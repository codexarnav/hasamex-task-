import React from "react";
import { Expert, Transcript } from "@/lib/types";
import { StatusBadge } from "../ui/StatusBadge";
import { User, Building2, Globe, FileText } from "lucide-react";

interface ExpertCardProps {
  expert: Expert;
  transcript?: Transcript;
}

export function ExpertCard({ expert, transcript }: ExpertCardProps) {
  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-xs transition-all hover:border-slate-300">
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-700 font-semibold text-sm">
            {expert.name
              .split(" ")
              .map((n) => n[0])
              .join("")
              .slice(0, 2)}
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">{expert.name}</h3>
            {expert.role && (
              <p className="text-xs text-muted-foreground">{expert.role}</p>
            )}
          </div>
        </div>

        {expert.market && (
          <span className="inline-flex items-center gap-1 rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
            <Globe className="h-3 w-3 text-slate-400" />
            {expert.market}
          </span>
        )}
      </div>

      <div className="space-y-2 pt-3 border-t border-border text-xs text-muted-foreground">
        {expert.organization && (
          <div className="flex items-center gap-2">
            <Building2 className="h-3.5 w-3.5 text-slate-400 shrink-0" />
            <span className="truncate">{expert.organization}</span>
          </div>
        )}

        <div className="flex items-center justify-between pt-1">
          <div className="flex items-center gap-2">
            <FileText className="h-3.5 w-3.5 text-slate-400 shrink-0" />
            <span className="truncate">{transcript?.file_name || "Transcript"}</span>
          </div>
          <StatusBadge status={transcript?.status || "ready"} />
        </div>
      </div>
    </div>
  );
}
