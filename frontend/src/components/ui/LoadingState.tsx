import React from "react";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

interface LoadingStateProps {
  message?: string;
  className?: string;
}

export function LoadingState({ message = "Loading research data...", className }: LoadingStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-12 text-center text-muted-foreground",
        className
      )}
    >
      <Loader2 className="h-6 w-6 animate-spin mb-3 text-slate-600" />
      <p className="text-sm font-medium">{message}</p>
    </div>
  );
}
