import React from "react";
import { StatusBadge } from "../ui/StatusBadge";
import { ProjectStatus } from "@/lib/types";

interface ProjectHeaderProps {
  title: string;
  description?: string | null;
  status?: ProjectStatus;
  actions?: React.ReactNode;
}

export function ProjectHeader({
  title,
  description,
  status,
  actions,
}: ProjectHeaderProps) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between pb-6 mb-6 border-b border-border">
      <div className="space-y-1.5 max-w-3xl">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">{title}</h1>
          {status && <StatusBadge status={status} />}
        </div>
        {description && (
          <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-2 shrink-0">{actions}</div>}
    </div>
  );
}
