import React from "react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string | number;
  description?: string;
  className?: string;
}

export function StatCard({ label, value, description, className }: StatCardProps) {
  return (
    <div
      className={cn(
        "rounded-lg border border-border bg-card p-5 shadow-sm transition-all hover:border-slate-300",
        className
      )}
    >
      <div className="text-3xl font-semibold tracking-tight text-foreground">{value}</div>
      <div className="text-xs font-medium uppercase tracking-wider text-muted-foreground mt-1">
        {label}
      </div>
      {description && <div className="text-xs text-muted-foreground mt-2">{description}</div>}
    </div>
  );
}
