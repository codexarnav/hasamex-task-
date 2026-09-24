"use client";

import React, { useState, useEffect } from "react";
import { ProjectHeader } from "@/components/layout/ProjectHeader";
import { QuestionCard } from "@/components/domain/QuestionCard";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { ResearchQuestion, Answer } from "@/lib/types";
import { api } from "@/lib/api";
import { HelpCircle } from "lucide-react";

export default function QuestionsListPage({
  params,
}: {
  params: { projectId: string };
}) {
  const { projectId } = params;
  const [questions, setQuestions] = useState<ResearchQuestion[]>([]);
  const [perspectiveCounts, setPerspectiveCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      setError(null);
      const [qRes, analysisRes] = await Promise.allSettled([
        api.getQuestions(projectId),
        api.getAnalysis(projectId),
      ]);

      if (qRes.status === "fulfilled") {
        setQuestions(qRes.value.questions || []);
      }

      if (analysisRes.status === "fulfilled" && analysisRes.value.questions) {
        const counts: Record<string, number> = {};
        analysisRes.value.questions.forEach((aq) => {
          counts[aq.question_id] = aq.answers?.length || 0;
        });
        setPerspectiveCounts(counts);
      }
    } catch (err: any) {
      setError(err.detail || err.message || "Failed to load questions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, [projectId]);

  if (loading) {
    return <LoadingState message="Loading research questions..." />;
  }

  if (error) {
    return (
      <ErrorState
        title="Could not load research questions"
        message={error}
        onRetry={fetchQuestions}
      />
    );
  }

  return (
    <div className="space-y-6 pb-12">
      <ProjectHeader
        title="Research Questions"
        description="Questions extracted dynamically from the interview guide with synthesized answers across all interviewed experts."
      />

      {questions.length === 0 ? (
        <EmptyState
          title="No research questions yet"
          description="Upload an interview guide in the Files section to automatically extract research inquiries using Gemini."
          icon={HelpCircle}
          actionLabel="Go to Files & Upload Guide"
          onAction={() => (window.location.href = `/projects/${projectId}/files`)}
        />
      ) : (
        <div className="space-y-4">
          {questions.map((q) => (
            <QuestionCard
              key={q.id}
              question={q}
              projectId={projectId}
              perspectiveCount={perspectiveCounts[q.id] ?? 0}
            />
          ))}
        </div>
      )}
    </div>
  );
}
