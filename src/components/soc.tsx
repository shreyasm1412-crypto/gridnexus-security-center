import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import type { Severity, Status } from "@/data/mock";

export function Panel({ title, action, className, children }: { title?: string; action?: ReactNode; className?: string; children: ReactNode }) {
  return (
    <section className={cn("rounded-lg border bg-card p-5 shadow-sm", className)}>
      {title && (
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-base font-semibold tracking-tight">{title}</h2>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

export function Metric({ label, value, sub, tone }: { label: string; value: ReactNode; sub?: ReactNode; tone?: Status }) {
  return (
    <div className="rounded-lg border bg-card p-4 shadow-sm">
      <div className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className={cn("mt-2 text-2xl font-semibold tabular-nums", tone && toneText[tone])}>{value}</div>
      {sub && <div className="mt-1 text-xs text-muted-foreground">{sub}</div>}
    </div>
  );
}

export const toneText: Record<Status, string> = {
  normal: "text-safe",
  warning: "text-warn",
  threat: "text-critical",
  offline: "text-offline",
};

export function Dot({ status, className }: { status: Status; className?: string }) {
  const map: Record<Status, string> = {
    normal: "bg-safe glow-safe",
    warning: "bg-warn glow-warn",
    threat: "bg-critical glow-critical",
    offline: "bg-offline",
  };
  return <span className={cn("inline-block h-2 w-2 shrink-0 rounded-full", map[status], className)} />;
}

export function SeverityBadge({ severity }: { severity: Severity }) {
  const map: Record<Severity, string> = {
    LOW: "border-energy/40 text-energy bg-energy/10",
    MEDIUM: "border-warn/40 text-warn bg-warn/10",
    HIGH: "border-critical/40 text-critical bg-critical/10",
    CRITICAL: "border-critical bg-critical text-destructive-foreground",
  };
  return <span className={cn("inline-flex rounded border px-2 py-0.5 text-[10px] font-semibold tracking-wider", map[severity])}>{severity}</span>;
}

export function StatusPill({ status }: { status: string }) {
  const tone =
    status === "Resolved" ? "text-safe border-safe/30" : status === "Contained" ? "text-energy border-energy/30" : status === "Investigating" ? "text-warn border-warn/30" : "text-critical border-critical/30";
  return <span className={cn("inline-flex rounded-full border px-2 py-0.5 text-[11px] font-medium", tone)}>{status}</span>;
}

export function PageHeading({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="mb-6">
      <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
      {subtitle && <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>}
    </div>
  );
}

export function riskTone(risk: number): Status {
  return risk >= 70 ? "threat" : risk >= 40 ? "warning" : "normal";
}
