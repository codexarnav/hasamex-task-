"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { Modal } from "../ui/Modal";
import { Utterance, Transcript } from "@/lib/types";
import { Clock, User } from "lucide-react";

interface TranscriptViewerProps {
  isOpen: boolean;
  onClose: () => void;
  transcript: Transcript | null;
  expertName?: string;
  utterances: Utterance[];
  highlightedUtteranceId?: string;
}

export function TranscriptViewer({
  isOpen,
  onClose,
  transcript,
  expertName,
  utterances,
  highlightedUtteranceId,
}: TranscriptViewerProps) {
  if (!transcript) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={transcript.file_name}
      description={`Transcript recording · ${expertName || "Expert Interview"}`}
      className="max-w-2xl"
    >
      <div className="max-h-[65vh] overflow-y-auto pr-2 space-y-4 divide-y divide-border/60">
        {utterances.map((utt) => {
          const isHighlighted =
            highlightedUtteranceId &&
            (utt.id === highlightedUtteranceId ||
              utt.text.includes(highlightedUtteranceId));

          return (
            <div
              key={utt.id || utt.sequence}
              className={cn(
                "pt-3 first:pt-0 transition-colors rounded-lg p-2.5",
                isHighlighted
                  ? "bg-amber-50/80 border border-amber-200 shadow-xs"
                  : "hover:bg-slate-50"
              )}
            >
              <div className="flex items-center justify-between text-xs text-muted-foreground mb-1.5">
                <div className="flex items-center gap-1.5 font-medium text-foreground">
                  <User className="h-3 w-3 text-slate-400" />
                  <span>{utt.speaker}</span>
                </div>
                {utt.timestamp_start && (
                  <div className="flex items-center gap-1 font-mono text-[11px] text-slate-400">
                    <Clock className="h-3 w-3" />
                    <span>
                      {utt.timestamp_start}
                      {utt.timestamp_end ? ` - ${utt.timestamp_end}` : ""}
                    </span>
                  </div>
                )}
              </div>
              <p className="text-xs leading-relaxed text-slate-700">{utt.text}</p>
            </div>
          );
        })}
      </div>
    </Modal>
  );
}
