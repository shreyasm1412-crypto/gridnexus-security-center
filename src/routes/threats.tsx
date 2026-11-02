import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { CheckCircle2 } from "lucide-react";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Metric, PageHeading, Panel, SeverityBadge, StatusPill, riskTone, toneText } from "@/components/soc";
import { alerts, threatSummary, type Alert } from "@/data/mock";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/threats")({
  head: () => ({
    meta: [
      { title: "Threat Detection — GridNexus AI" },
      { name: "description", content: "AI-assisted detection of cyber threats across smart grid devices." },
      { property: "og:title", content: "Threat Detection — GridNexus AI" },
      { property: "og:description", content: "AI-assisted detection of cyber threats across smart grid devices." },
    ],
  }),
  component: Threats,
});

function Threats() {
  const [sel, setSel] = useState<Alert | null>(null);
  return (
    <div className="space-y-6">
      <PageHeading title="Threat Detection Center" subtitle="Correlated alerts from rule-based and machine learning detectors" />
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
        <Metric label="Total Events" value={threatSummary.total.toLocaleString()} />
        <Metric label="Threats Detected" value={threatSummary.detected} tone="warning" />
        <Metric label="High Risk" value={threatSummary.high} tone="threat" />
        <Metric label="Critical" value={threatSummary.critical} />
      </div>
      <Panel title="Active Alerts">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-[11px] uppercase tracking-wider text-muted-foreground">
                {["Alert ID", "Time", "Device", "Threat Type", "Detection Method", "Confidence", "Severity", "Status"].map((h) => (
                  <th key={h} className="whitespace-nowrap px-3 py-2.5 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {alerts.map((a) => (
                <tr key={a.id} onClick={() => setSel(a)} className="cursor-pointer border-b last:border-0 hover:bg-accent/50">
                  <td className="px-3 py-3 font-mono text-xs text-primary">{a.id}</td>
                  <td className="px-3 py-3 font-mono text-xs text-muted-foreground">{a.time}</td>
                  <td className="px-3 py-3 font-mono text-xs">{a.device}</td>
                  <td className="whitespace-nowrap px-3 py-3">{a.type}</td>
                  <td className="whitespace-nowrap px-3 py-3 text-muted-foreground">{a.method}</td>
                  <td className="px-3 py-3 tabular-nums">{a.confidence}%</td>
                  <td className="px-3 py-3"><SeverityBadge severity={a.severity} /></td>
                  <td className="px-3 py-3"><StatusPill status={a.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <Sheet open={!!sel} onOpenChange={(o) => !o && setSel(null)}>
        <SheetContent className="w-[420px] overflow-y-auto sm:max-w-md">
          {sel && (
            <>
              <SheetHeader>
                <SheetTitle className="flex items-center gap-3"><span className="font-mono">{sel.id}</span><SeverityBadge severity={sel.severity} /></SheetTitle>
              </SheetHeader>
              <div className="space-y-6 px-4 pb-6">
                <Section title="Threat Summary">
                  <div className="mb-1 text-sm font-medium">{sel.type} · <span className="font-mono">{sel.device}</span></div>
                  <p className="text-sm leading-relaxed text-muted-foreground">{sel.summary}</p>
                </Section>
                <Section title="Detection Evidence">
                  <ul className="space-y-2">
                    {sel.evidence.map((e) => (
                      <li key={e} className="flex gap-2 rounded-md border bg-background/40 px-3 py-2 text-sm"><span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-warn" />{e}</li>
                    ))}
                  </ul>
                </Section>
                <div className="grid grid-cols-2 gap-3">
                  <Section title="AI Confidence">
                    <div className="text-2xl font-semibold tabular-nums">{sel.confidence}%</div>
                    <div className="mt-2 h-1.5 rounded-full bg-muted"><div className="h-full rounded-full bg-primary" style={{ width: `${sel.confidence}%` }} /></div>
                    <div className="mt-1 text-[11px] text-muted-foreground">{sel.method}</div>
                  </Section>
                  <Section title="Risk Score">
                    <div className={cn("text-2xl font-semibold tabular-nums", toneText[riskTone(sel.risk)])}>{sel.risk}<span className="text-sm text-muted-foreground">/100</span></div>
                  </Section>
                </div>
                <Section title="Recommended Response">
                  <ol className="space-y-2">
                    {sel.response.map((r) => (
                      <li key={r} className="flex items-center gap-2 text-sm"><CheckCircle2 className="h-4 w-4 text-primary" />{r}</li>
                    ))}
                  </ol>
                </Section>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">{title}</h3>
      {children}
    </div>
  );
}
