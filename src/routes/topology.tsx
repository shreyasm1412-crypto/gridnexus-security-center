import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Zap, Building2, GitBranch, Gauge } from "lucide-react";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Dot, PageHeading, Panel, riskTone, toneText } from "@/components/soc";
import { attackScenarios, topologyNodes, type GridNode, type Status } from "@/data/mock";
import { useSimulation } from "@/lib/simulation";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/topology")({
  head: () => ({
    meta: [
      { title: "Grid Topology — GridNexus AI" },
      { name: "description", content: "Interactive digital twin of the simulated smart grid infrastructure." },
      { property: "og:title", content: "Grid Topology — GridNexus AI" },
      { property: "og:description", content: "Interactive digital twin of the simulated smart grid infrastructure." },
    ],
  }),
  component: Topology,
});

// Positions in a 1000x560 coordinate space
const pos: Record<string, [number, number]> = {
  "PS-01": [500, 50], "SUB-01": [500, 170], "FDR-A": [270, 310], "FDR-B": [730, 310],
  "SM-01": [130, 470], "SM-02": [270, 470], "SM-03": [410, 470],
  "SM-04": [590, 470], "SM-05": [730, 470], "SM-06": [870, 470],
};
const edges: [string, string][] = [
  ["PS-01", "SUB-01"], ["SUB-01", "FDR-A"], ["SUB-01", "FDR-B"],
  ["FDR-A", "SM-01"], ["FDR-A", "SM-02"], ["FDR-A", "SM-03"],
  ["FDR-B", "SM-04"], ["FDR-B", "SM-05"], ["FDR-B", "SM-06"],
];
const icons = { "Power Source": Zap, Substation: Building2, Feeder: GitBranch, "Smart Meter": Gauge };
const statusLabel: Record<Status, string> = { normal: "Normal", warning: "Warning", threat: "Threat", offline: "Offline" };

function Topology() {
  const { attack } = useSimulation();
  const target = attackScenarios[attack].target;
  const parent = edges.find(([, c]) => c === target)?.[0];
  const statusOf = (id: string): Status => (id === target ? "threat" : id === parent ? "warning" : "normal");
  const [selected, setSelected] = useState<GridNode | null>(null);

  const strokeFor = (s: Status) => (s === "threat" ? "var(--critical)" : s === "warning" ? "var(--warn)" : "var(--energy)");

  return (
    <div>
      <PageHeading title="Smart Grid Digital Twin" subtitle="Real-time simulated infrastructure monitoring" />
      <Panel
        action={
          <div className="flex gap-4 text-xs text-muted-foreground">
            {(["normal", "warning", "threat", "offline"] as Status[]).map((s) => (
              <span key={s} className="flex items-center gap-1.5"><Dot status={s} />{statusLabel[s]}</span>
            ))}
          </div>
        }
        title="Infrastructure Map"
      >
        <div className="relative mx-auto aspect-[1000/560] w-full max-w-5xl">
          <svg viewBox="0 0 1000 560" className="absolute inset-0 h-full w-full">
            {edges.map(([a, b]) => {
              const [x1, y1] = pos[a];
              const [x2, y2] = pos[b];
              const s = statusOf(b);
              return (
                <g key={a + b}>
                  <path d={`M${x1},${y1} V${(y1 + y2) / 2} H${x2} V${y2}`} fill="none" stroke="var(--border)" strokeWidth={2} />
                  <path d={`M${x1},${y1} V${(y1 + y2) / 2} H${x2} V${y2}`} fill="none" stroke={strokeFor(s)} strokeOpacity={0.7} strokeWidth={1.5} className="flow-line" />
                </g>
              );
            })}
          </svg>
          {topologyNodes.map((n) => {
            const [x, y] = pos[n.id];
            const s = statusOf(n.id);
            const Icon = icons[n.type];
            return (
              <button
                key={n.id}
                onClick={() => setSelected(n)}
                style={{ left: `${x / 10}%`, top: `${(y / 560) * 100}%` }}
                className={cn(
                  "absolute flex -translate-x-1/2 -translate-y-1/2 items-center gap-2 rounded-md border bg-card px-3 py-2 text-left shadow-md transition-colors hover:border-primary",
                  s === "threat" && "border-critical/70",
                  s === "warning" && "border-warn/60",
                )}
              >
                <Icon className={cn("h-4 w-4", s === "normal" ? "text-energy" : toneText[s])} />
                <div className="leading-tight">
                  <div className="whitespace-nowrap text-xs font-semibold">{n.type === "Smart Meter" ? n.id : n.label}</div>
                  <div className="hidden text-[10px] text-muted-foreground sm:block">{n.type === "Smart Meter" ? "Smart Meter" : n.id}</div>
                </div>
                <Dot status={s} className="ml-1" />
              </button>
            );
          })}
        </div>
      </Panel>

      <Sheet open={!!selected} onOpenChange={(o) => !o && setSelected(null)}>
        <SheetContent className="w-[360px] sm:max-w-sm">
          {selected && (() => {
            const s = statusOf(selected.id);
            const risk = s === "threat" ? attackScenarios[attack].risk : s === "warning" ? 48 : selected.risk;
            const rows: [string, React.ReactNode][] = [
              ["Device ID", <span className="font-mono">{selected.id}</span>],
              ["Device Type", selected.type],
              ["Voltage", selected.voltage],
              ["Current", selected.current],
              ["Frequency", selected.frequency],
              ["Power", selected.power],
              ["Network Latency", `${s === "threat" ? attackScenarios[attack].latency : selected.latency} ms`],
              ["Security Status", <span className={cn("flex items-center gap-2", toneText[s])}><Dot status={s} />{statusLabel[s]}</span>],
              ["Risk Score", <span className={toneText[riskTone(risk)]}>{risk}/100</span>],
            ];
            return (
              <>
                <SheetHeader><SheetTitle>{selected.label}</SheetTitle></SheetHeader>
                <dl className="mt-4 divide-y px-4">
                  {rows.map(([k, v]) => (
                    <div key={k} className="flex items-center justify-between py-3 text-sm">
                      <dt className="text-muted-foreground">{k}</dt>
                      <dd className="font-medium tabular-nums">{v}</dd>
                    </div>
                  ))}
                </dl>
              </>
            );
          })()}
        </SheetContent>
      </Sheet>
    </div>
  );
}
