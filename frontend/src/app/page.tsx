"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Project } from "@/lib/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { Plus, ArrowRight, FolderKanban } from "lucide-react";

export default function ProjectListPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getProjects();
      setProjects(res.projects || []);
    } catch (err: any) {
      setError(err.detail || err.message || "Failed to load projects from backend API");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  return (
    <div className="min-h-screen bg-background p-6 sm:p-10 lg:p-12">
      <div className="mx-auto max-w-4xl space-y-8">
        {}
        <div className="flex items-center justify-between pb-6 border-b border-border">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded bg-slate-900 text-white text-xs font-bold">
                OS
              </div>
              <span className="text-sm font-semibold tracking-tight text-foreground">
                InsightOS
              </span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground pt-1">
              Research Projects
            </h1>
            <p className="text-xs text-muted-foreground">
              Qualitative intelligence and grounded transcript analysis
            </p>
          </div>

          <Link href="/projects/new">
            <Button size="sm" className="flex items-center gap-1.5 shadow-sm">
              <Plus className="h-4 w-4" />
              <span>New Project</span>
            </Button>
          </Link>
        </div>

        {}
        {loading ? (
          <LoadingState message="Connecting to InsightOS API..." />
        ) : error ? (
          <ErrorState
            title="Could not load projects"
            message={error}
            onRetry={fetchProjects}
          />
        ) : projects.length === 0 ? (
          <EmptyState
            title="No research projects yet"
            description="Create your first research project to upload an interview guide and analyze expert transcripts."
            icon={FolderKanban}
            actionLabel="Create Project"
            onAction={() => (window.location.href = "/projects/new")}
          />
        ) : (
          <div className="space-y-4">
            {projects.map((project) => (
              <div
                key={project.id}
                className="group rounded-xl border border-border bg-card p-6 shadow-xs transition-all hover:border-slate-300 hover:shadow-sm"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-3">
                      <h2 className="text-lg font-semibold text-foreground group-hover:text-slate-900 transition-colors">
                        {project.name}
                      </h2>
                      <StatusBadge status={project.status} />
                    </div>

                    {project.objective && (
                      <p className="text-xs text-muted-foreground line-clamp-2 max-w-2xl leading-relaxed">
                        {project.objective}
                      </p>
                    )}

                    <div className="flex items-center gap-4 text-xs text-muted-foreground pt-1">
                      <span className="font-mono text-[11px] text-slate-400">
                        ID: {project.id.slice(0, 8)}
                      </span>
                    </div>
                  </div>

                  <Link
                    href={`/projects/${project.id}`}
                    className="inline-flex items-center justify-center gap-1.5 rounded-md bg-slate-900 px-4 py-2 text-xs font-medium text-white shadow-sm hover:bg-slate-800 transition-colors shrink-0"
                  >
                    <span>Open project</span>
                    <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
