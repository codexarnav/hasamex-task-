"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { ArrowLeft, Sparkles, Loader2, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

export default function CreateProjectPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [objective, setObjective] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      setLoading(true);
      setError(null);
      const project = await api.createProject({
        name: name.trim(),
        objective: objective.trim() || null,
      });
      router.push(`/projects/${project.id}/files`);
    } catch (err: any) {
      setError(err.detail || err.message || "Failed to create project");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-6 sm:p-10 lg:p-12">
      <div className="mx-auto max-w-xl space-y-6">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Back to all projects</span>
        </Link>

        <div className="rounded-xl border border-border bg-card p-8 shadow-sm space-y-6">
          <div className="space-y-1.5">
            <h1 className="text-xl font-bold tracking-tight text-foreground">
              Create Research Project
            </h1>
            <p className="text-xs text-muted-foreground">
              Define your qualitative research study scope and primary inquiries.
            </p>
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 rounded-md bg-rose-50 border border-rose-200 text-rose-700 text-xs">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <label htmlFor="name" className="text-xs font-semibold text-foreground">
                Project Name <span className="text-rose-500">*</span>
              </label>
              <Input
                id="name"
                required
                disabled={loading}
                placeholder="e.g., Robotic Surgery Adoption in European Hospitals"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="text-sm"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="objective" className="text-xs font-semibold text-foreground">
                Research Objective
              </label>
              <Textarea
                id="objective"
                rows={4}
                disabled={loading}
                placeholder="Describe the primary research thesis, target hospital markets, and key hypotheses to validate..."
                value={objective}
                onChange={(e) => setObjective(e.target.value)}
                className="text-sm leading-relaxed"
              />
              <p className="text-[11px] text-muted-foreground">
                The objective will guide strategic insight synthesis and cross-expert divergence detection.
              </p>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-border">
              <Link href="/">
                <Button variant="outline" type="button" size="sm" disabled={loading}>
                  Cancel
                </Button>
              </Link>
              <Button type="submit" size="sm" disabled={loading} className="flex items-center gap-1.5 shadow-sm">
                {loading ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    <span>Creating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="h-3.5 w-3.5" />
                    <span>Create Project</span>
                  </>
                )}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
