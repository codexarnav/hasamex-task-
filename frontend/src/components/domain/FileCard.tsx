import React from "react";
import { StatusBadge } from "../ui/StatusBadge";
import { FileText, Clock, User, Globe, Trash2, Check } from "lucide-react";
import { Button } from "../ui/Button";

interface FileCardProps {
  type: "guide" | "transcript";
  fileName: string;
  status: string;
  expertName?: string;
  market?: string;
  duration?: string | null;
  uploadedAt?: string;
  onDelete?: () => void;
  isSelected?: boolean;
  onToggleSelect?: () => void;
}

export function FileCard({
  type,
  fileName,
  status,
  expertName,
  market,
  duration,
  uploadedAt,
  onDelete,
  isSelected,
  onToggleSelect,
}: FileCardProps) {
  return (
    <div
      className={`rounded-xl border bg-card p-4 shadow-xs flex items-center justify-between gap-4 transition-all ${
        isSelected
          ? "border-emerald-400 bg-emerald-50/30 ring-1 ring-emerald-200"
          : "border-border hover:border-slate-300"
      }`}
    >
      <div className="flex items-center gap-3.5 min-w-0">
        {onToggleSelect ? (
          <button
            type="button"
            onClick={onToggleSelect}
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg transition-all cursor-pointer ${
              isSelected
                ? "bg-emerald-500 text-white shadow-sm"
                : "bg-slate-100 text-slate-400 hover:bg-slate-200 hover:text-slate-600"
            }`}
          >
            {isSelected ? (
              <Check className="h-5 w-5" strokeWidth={3} />
            ) : (
              <FileText className="h-5 w-5" />
            )}
          </button>
        ) : (
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-700">
            <FileText className="h-5 w-5" />
          </div>
        )}
        <div className="min-w-0 space-y-0.5">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-semibold text-foreground truncate">{fileName}</h4>
            <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
              {type === "guide" ? "Interview Guide" : "Transcript"}
            </span>
          </div>

          <div className="flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
            {expertName && (
              <span className="flex items-center gap-1 font-medium text-slate-700">
                <User className="h-3 w-3 text-slate-400" />
                {expertName}
              </span>
            )}
            {market && (
              <span className="flex items-center gap-1">
                <Globe className="h-3 w-3 text-slate-400" />
                {market}
              </span>
            )}
            {duration && (
              <span className="flex items-center gap-1 font-mono">
                <Clock className="h-3 w-3 text-slate-400" />
                {duration}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        <StatusBadge status={status} />
        {onDelete && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onDelete}
            className="h-8 w-8 text-muted-foreground hover:text-rose-600"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}
