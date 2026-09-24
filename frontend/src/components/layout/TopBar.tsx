"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { StatusBadge } from "../ui/StatusBadge";
import { Button } from "../ui/Button";
import { Menu, ChevronRight } from "lucide-react";
import { ProjectStatus } from "@/lib/types";

interface TopBarProps {
  projectId: string;
  projectName?: string;
  projectStatus?: ProjectStatus;
  onMobileMenuToggle?: () => void;
}

export function TopBar({
  projectId,
  projectName = "Robotic Surgery Adoption",
  projectStatus = "completed",
  onMobileMenuToggle,
}: TopBarProps) {
  const pathname = usePathname();

  const segments = pathname.split("/").filter(Boolean);
  const currentSection = segments[2] || "Overview";
  const formattedSection =
    currentSection.charAt(0).toUpperCase() + currentSection.slice(1);

  return (
    <header className="flex h-14 w-full items-center justify-between border-b border-border bg-card px-4 sm:px-6">
      <div className="flex items-center gap-3">
        {onMobileMenuToggle && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onMobileMenuToggle}
            className="md:hidden h-8 w-8 text-muted-foreground"
          >
            <Menu className="h-4 w-4" />
          </Button>
        )}

        {}
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Link
            href={`/projects/${projectId}`}
            className="font-medium text-foreground hover:underline truncate max-w-[200px] sm:max-w-[320px]"
          >
            {projectName}
          </Link>
          <ChevronRight className="h-3 w-3 shrink-0 text-slate-400" />
          <span className="text-slate-600 font-medium">{formattedSection}</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <StatusBadge status={projectStatus} />
      </div>
    </header>
  );
}
