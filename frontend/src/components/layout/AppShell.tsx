"use client";

import React, { useState, useEffect } from "react";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { ProjectStatus } from "@/lib/types";
import { api } from "@/lib/api";

interface AppShellProps {
  projectId: string;
  projectName?: string;
  projectStatus?: ProjectStatus;
  children: React.ReactNode;
}

export function AppShell({
  projectId,
  projectName = "Research Project",
  projectStatus = "pending",
  children,
}: AppShellProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [projectData, setProjectData] = useState<{ name: string; status: ProjectStatus } | null>(null);

  useEffect(() => {
    if (projectId && projectId !== "proj-1") {
      api.getProject(projectId)
        .then((p) => {
          setProjectData({ name: p.name, status: p.status as ProjectStatus });
        })
        .catch(() => {});
    }
  }, [projectId]);

  const activeName = projectData?.name || projectName;
  const activeStatus = projectData?.status || projectStatus;

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background">
      {}
      <div className="hidden md:flex shrink-0">
        <Sidebar projectId={projectId} projectName={activeName} />
      </div>

      {}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          <div
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="relative z-50 w-60 h-full bg-card shadow-2xl">
            <Sidebar projectId={projectId} projectName={activeName} />
          </div>
        </div>
      )}

      {}
      <div className="flex flex-1 flex-col min-w-0 overflow-hidden">
        <TopBar
          projectId={projectId}
          projectName={activeName}
          projectStatus={activeStatus}
          onMobileMenuToggle={() => setMobileMenuOpen(!mobileMenuOpen)}
        />
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="mx-auto max-w-5xl">{children}</div>
        </main>
      </div>
    </div>
  );
}
