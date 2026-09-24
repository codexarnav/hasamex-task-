"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  HelpCircle,
  Users,
  Quote,
  GitCompare,
  Lightbulb,
  Sparkles,
  Files,
  ArrowLeft,
} from "lucide-react";

interface SidebarProps {
  projectId: string;
  projectName?: string;
  className?: string;
}

export function Sidebar({ projectId, className }: SidebarProps) {
  const pathname = usePathname();

  const mainNavItems = [
    {
      name: "Overview",
      href: `/projects/${projectId}`,
      icon: LayoutDashboard,
      exact: true,
    },
    {
      name: "Questions",
      href: `/projects/${projectId}/questions`,
      icon: HelpCircle,
    },
    {
      name: "Experts",
      href: `/projects/${projectId}/experts`,
      icon: Users,
    },
    {
      name: "Evidence",
      href: `/projects/${projectId}/evidence`,
      icon: Quote,
    },
    {
      name: "Differences",
      href: `/projects/${projectId}/differences`,
      icon: GitCompare,
    },
    {
      name: "Insights",
      href: `/projects/${projectId}/insights`,
      icon: Lightbulb,
    },
  ];

  const copilotNav = [
    {
      name: "Copilot",
      href: `/projects/${projectId}/copilot`,
      icon: Sparkles,
    },
  ];

  const filesNav = [
    {
      name: "Files",
      href: `/projects/${projectId}/files`,
      icon: Files,
    },
  ];

  const isLinkActive = (href: string, exact?: boolean) => {
    if (exact) {
      return pathname === href;
    }
    return pathname.startsWith(href);
  };

  return (
    <aside
      className={cn(
        "flex h-screen w-60 flex-col border-r border-border bg-card select-none shrink-0",
        className
      )}
    >
      {/* Brand Header */}
      <div className="flex h-14 items-center justify-between border-b border-border px-4">
        <Link href="/" className="flex items-center gap-2 text-foreground font-semibold tracking-tight">
          <div className="flex h-6 w-6 items-center justify-center rounded bg-slate-900 text-white text-xs font-bold">
            OS
          </div>
          <span className="text-sm">InsightOS</span>
        </Link>
        <Link
          href="/"
          className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors"
          title="All Projects"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Projects</span>
        </Link>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        <div>
          <div className="px-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-1">
            Analysis
          </div>
          <nav className="space-y-0.5">
            {mainNavItems.map((item) => {
              const active = isLinkActive(item.href, item.exact);
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors",
                    active
                      ? "bg-slate-100 text-slate-900 font-semibold shadow-xs"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  )}
                >
                  <Icon className={cn("h-4 w-4", active ? "text-slate-900" : "text-slate-500")} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div>
          <div className="px-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-1">
            Intelligence
          </div>
          <nav className="space-y-0.5">
            {copilotNav.map((item) => {
              const active = isLinkActive(item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors",
                    active
                      ? "bg-slate-100 text-slate-900 font-semibold shadow-xs"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  )}
                >
                  <Icon className={cn("h-4 w-4", active ? "text-slate-900" : "text-slate-500")} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div>
          <div className="px-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-1">
            Source Data
          </div>
          <nav className="space-y-0.5">
            {filesNav.map((item) => {
              const active = isLinkActive(item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors",
                    active
                      ? "bg-slate-100 text-slate-900 font-semibold shadow-xs"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  )}
                >
                  <Icon className={cn("h-4 w-4", active ? "text-slate-900" : "text-slate-500")} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-border p-3">
        <div className="px-2 py-1.5 rounded bg-slate-50 border border-slate-200/60">
          <div className="text-[11px] font-medium text-slate-800">InsightOS V1</div>
          <div className="text-[10px] text-slate-500">Evidence-Grounded Intelligence</div>
        </div>
      </div>
    </aside>
  );
}
