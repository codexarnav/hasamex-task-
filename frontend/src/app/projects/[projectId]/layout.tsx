import React from "react";
import { AppShell } from "@/components/layout/AppShell";

interface ProjectLayoutProps {
  children: React.ReactNode;
  params: {
    projectId: string;
  };
}

export default function ProjectLayout({ children, params }: ProjectLayoutProps) {
  return (
    <AppShell projectId={params.projectId}>
      {children}
    </AppShell>
  );
}
