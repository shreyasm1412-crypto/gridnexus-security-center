import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { CheckCircle2 } from "lucide-react";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Metric, PageHeading, SeverityBadge, StatusPill, riskTone, toneText } from "@/components/soc";
import { incidentResponses, incidentStages, incidents as mockIncidents, type Incident } from "@/data/mock";
import { fetchIncidents, updateIncidentStatus } from "@/lib/api";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/incidents")({
  head: () => ({
    meta: [
      { title: "Incident Management — GridNexus AI" },
      { name: "description", content: "Track and respond to smart grid security incidents." },
      { property: "og:title", content: "Incident Management — GridNexus AI" },
      { property: "og:description", content: "Track and respond to smart grid security incidents." },
    ],
  }),
  component: Incidents,
});

const stageIndex: Record<Incident["status"], number> = { Open: 0, Investigating: 1, Contained: 2, Resolved: 3 };

function Incidents() {
  const [incidentsList, setIncidentsList] = useState<Incident[]>(mockIncidents);
  const [sel, setSel] = useState<Incident | null>(null);

  useEffect(() => {
    let mounted = true;
    const poll = async () => {
      try {
        const data = await fetchIncidents();
        if (mounted && data) {
          setIncidentsList(data);
          // Keep sel synced if selected
          if (sel) {
            const freshSel = data.find((x) => x.id === sel.id);
            if (freshSel) setSel(freshSel);
          }
        }
      } catch (err) {
        console.warn("Polling /api/incidents failed:", err);
      }
    };
    poll();
    const interval = setInterval(poll, 2000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [sel?.id]);

  const count = (s: Incident["status"]) => incidentsList.filter((i) => i.status === s).length;

  const handleStatusChange = async (newStatus: Incident["status"]) => {
    if (!sel) return;
    try {
      const updated = await updateIncidentStatus(sel.id, newStatus);
      if (updated) {
        setSel(updated);
        setIncidentsList((prev) => prev.map((item) => (item.id === sel.id ? updated : item)));
      } else {
        // Optimistic update if backend offline
        const updatedLocal = { ...sel, status: newStatus };
        setSel(updatedLocal);
        setIncidentsList((prev) => prev.map((item) => (item.id === sel.id ? updatedLocal : item)));
      }
    } catch (err) {
      console.warn("Updating incident status failed:", err);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeading title="Incident Response Center" subtitle="Incident lifecycle and recommended response actions" />
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
        <Metric label="Open" value={count("Open")} tone="threat" />
        <Metric label="Investigating" value={count("Investigating")} tone="warning" />
        <Metric label="Contained" value={count("Contained")} />
        <Metric label="Resolved" value={count("Resolved")} tone="normal" />
      </div>

      <div className="space-y-3">
        {incidentsList.map((i) => (
          <button
            key={i.id}
            onClick={() => setSel(i)}
            className="grid w-full grid-cols-2 items-center gap-4 rounded-lg border bg-card px-5 py-4 text-left shadow-sm transition-colors hover:border-primary/60 md:grid-cols-7"
          >
            <Field label="Incident ID"><span className="font-mono text-primary">{i.id}</span></Field>
            <Field label="Threat Type">{i.type}</Field>
            <Field label="Affected Device"><span className="font-mono">{i.device}</span></Field>
            <Field label="Severity"><SeverityBadge severity={i.severity} /></Field>
            <Field label="Detection Time"><span className="font-mono text-xs">{i.time}</span></Field>
            <Field label="Risk Score"><span className={toneText[riskTone(i.risk)]}>{i.risk}/100</span></Field>
            <Field label="Current Status"><StatusPill status={i.status} /></Field>
          </button>
        ))}
      </div>

      <Sheet open={!!sel} onOpenChange={(o) => !o && setSel(null)}>
        <SheetContent className="w-[400px] overflow-y-auto sm:max-w-md">
          {sel && (
            <>
              <SheetHeader>
                <SheetTitle className="flex items-center gap-3"><span className="font-mono">{sel.id}</span><SeverityBadge severity={sel.severity} /></SheetTitle>
                <p className="text-sm text-muted-foreground">{sel.type} · <span className="font-mono">{sel.device}</span></p>
              </SheetHeader>
              <div className="space-y-6 px-4 pb-6">
                <div>
                  <h3 className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Incident Timeline</h3>
                  <ol className="relative ml-1.5 border-l">
                    {incidentStages.map((st, idx) => {
                      const done = idx <= stageIndex[sel.status];
                      return (
                        <li key={st} className="mb-5 ml-5 last:mb-0">
                          <span className={cn("absolute -left-[6px] mt-1 h-3 w-3 rounded-full border-2", done ? "border-primary bg-primary" : "border-border bg-background")} />
                          <div className={cn("text-sm font-medium", !done && "text-muted-foreground")}>{idx + 1}. {st}</div>
                          <div className="text-xs text-muted-foreground">{done ? (idx === stageIndex[sel.status] ? "Current stage" : "Completed") : "Pending"}</div>
                        </li>
                      );
                    })}
                  </ol>
                </div>
                <div>
                  <h3 className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Recommended Response</h3>
                  <ul className="space-y-2">
                    {(incidentResponses[sel.type] || []).map((r) => (
                      <li key={r} className="flex items-center gap-2 rounded-md border bg-background/40 px-3 py-2 text-sm"><CheckCircle2 className="h-4 w-4 text-primary" />{r}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Update Incident Status</h3>
                  <div className="flex flex-wrap gap-2">
                    {(["Open", "Investigating", "Contained", "Resolved"] as Incident["status"][]).map((st) => (
                      <button
                        key={st}
                        disabled={sel.status === st}
                        onClick={() => handleStatusChange(st)}
                        className={cn(
                          "rounded border px-2.5 py-1 text-xs font-medium transition-colors cursor-pointer",
                          sel.status === st
                            ? "border-primary bg-primary/20 text-primary cursor-default pointer-events-none"
                            : "hover:border-primary/60 hover:bg-accent"
                        )}
                      >
                        {st}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="min-w-0">
      <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="mt-1 truncate text-sm">{children}</div>
    </div>
  );
}
