import React from "react";
import { cn } from "@/lib/utils";
import { ProjectStatus, GuideStatus, TranscriptStatus, AnalysisStatus } from "@/lib/types";

type AnyStatus = ProjectStatus | GuideStatus | TranscriptStatus | AnalysisStatus | string;

interface StatusBadgeProps {
  status: AnyStatus;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const normalized = status.toLowerCase();

  let colorClasses = "bg-slate-100 text-slate-700 border-slate-200";
  let label = status;

  if (["completed", "ready"].includes(normalized)) {
    colorClasses = "bg-emerald-50 text-emerald-700 border-emerald-200";
    label = normalized === "ready" ? "Ready" : "Analysis Complete";
  } else if (
    ["processing", "parsing", "embedding", "retrieving", "classifying", "generating"].includes(
      normalized
    )
  ) {
    colorClasses = "bg-amber-50 text-amber-700 border-amber-200 animate-pulse";
    label = normalized.charAt(0).toUpperCase() + normalized.slice(1);
  } else if (["failed"].includes(normalized)) {
    colorClasses = "bg-rose-50 text-rose-700 border-rose-200";
    label = "Failed";
  } else if (["uploaded"].includes(normalized)) {
    colorClasses = "bg-blue-50 text-blue-700 border-blue-200";
    label = "Uploaded";
  } else if (["pending"].includes(normalized)) {
    colorClasses = "bg-slate-100 text-slate-600 border-slate-200";
    label = "Pending";
  }

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border",
        colorClasses,
        className
      )}
    >
      <span
        className={cn(
          "w-1.5 h-1.5 rounded-full",
          ["completed", "ready"].includes(normalized)
            ? "bg-emerald-500"
            : ["processing", "parsing", "embedding", "retrieving", "classifying", "generating"].includes(normalized)
            ? "bg-amber-500"
            : ["failed"].includes(normalized)
            ? "bg-rose-500"
            : "bg-slate-400"
        )}
      />
      {label}
    </span>
  );
}
