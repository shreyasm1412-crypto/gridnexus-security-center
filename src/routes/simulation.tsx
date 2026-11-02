import { createFileRoute } from "@tanstack/react-router";
import { Activity, Database, ServerCrash, KeyRound, RotateCcw, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dot, PageHeading, Panel, toneText } from "@/components/soc";
import { attackScenarios, simulationStages, type AttackKey, type Status } from "@/data/mock";
import { useSimulation } from "@/lib/simulation";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/simulation")({
  head: () => ({
    meta: [
      { title: "Attack Simulation — GridNexus AI" },
      { name: "description", content: "Controlled cyberattack simulation lab for smart grid security testing." },
      { property: "og:title", content: "Attack Simulation — GridNexus AI" },
      { property: "og:description", content: "Controlled cyberattack simulation lab for smart grid security testing." },
    ],
  }),
  component: Simulation,
});

const cards: { key: AttackKey; icon: typeof Activity }[] = [
  { key: "normal", icon: Activity },
  { key: "fdi", icon: Database },
  { key: "dos", icon: ServerCrash },
  { key: "ua", icon: KeyRound },
];

function Simulation() {
  const { attack, setAttack } = useSimulation();
  const sc = attackScenarios[attack];
  const isNormal = attack === "normal";

  const healthTone: Status = sc.gridHealth >= 90 ? "normal" : sc.gridHealth >= 80 ? "warning" : "threat";
  const latTone: Status = sc.latency < 30 ? "normal" : sc.latency < 100 ? "warning" : "threat";
  const confTone: Status = sc.confidence === 0 ? "normal" : sc.confidence >= 85 ? "threat" : "warning";
  const riskTone: Status = sc.risk < 40 ? "normal" : sc.risk < 75 ? "warning" : "threat";

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <PageHeading title="Cyberattack Simulation Lab" subtitle="Controlled Smart Grid Security Testing Environment" />
        <span className="rounded border border-warn/40 bg-warn/10 px-3 py-1.5 text-[11px] font-semibold tracking-wider text-warn">
          SIMULATION ONLY — NO REAL GRID SYSTEMS ARE CONNECTED
        </span>
      </div>

      <Panel>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Current Simulation Status</div>
            <div className={cn("mt-1 flex items-center gap-3 text-xl font-bold tracking-wide", isNormal ? "text-safe" : "text-critical")}>
              <Dot status={isNormal ? "normal" : "threat"} className="h-3 w-3" />
              {isNormal ? "NORMAL OPERATION" : `${sc.title.toUpperCase()} IN PROGRESS`}
            </div>
            {!isNormal && <div className="mt-1 text-xs text-muted-foreground">Target device: <span className="font-mono">{sc.target}</span></div>}
          </div>
          <Button variant="outline" onClick={() => setAttack("normal")} disabled={isNormal} className="gap-2">
            <RotateCcw className="h-4 w-4" /> RESET TO NORMAL
          </Button>
        </div>
      </Panel>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {cards.map(({ key, icon: Icon }) => {
          const s = attackScenarios[key];
          const active = attack === key;
          return (
            <button
              key={key}
              onClick={() => setAttack(key)}
              className={cn(
                "rounded-lg border bg-card p-5 text-left shadow-sm transition-colors hover:border-primary/60",
                active && (key === "normal" ? "border-safe/70 bg-safe/5" : "border-critical/70 bg-critical/5"),
              )}
            >
              <Icon className={cn("h-5 w-5", active ? (key === "normal" ? "text-safe" : "text-critical") : "text-energy")} />
              <div className="mt-3 text-sm font-semibold tracking-wide">{s.title.toUpperCase()}</div>
              <p className="mt-1 text-xs leading-relaxed text-muted-foreground">{s.description}</p>
            </button>
          );
        })}
      </div>

      <Panel title="Simulation Flow">
        <div className="flex flex-wrap items-center gap-2">
          {simulationStages.map((st, i) => {
            const reached = i <= sc.stage;
            const current = i === sc.stage;
            return (
              <div key={st} className="flex items-center gap-2">
                <div
                  className={cn(
                    "rounded-md border px-3 py-2 text-[11px] font-semibold tracking-wider transition-colors",
                    current && isNormal && "border-safe bg-safe/10 text-safe",
                    current && !isNormal && "border-critical bg-critical/10 text-critical",
                    reached && !current && "border-primary/50 bg-primary/10 text-primary",
                    !reached && "text-muted-foreground",
                  )}
                >
                  {st.toUpperCase()}
                </div>
                {i < simulationStages.length - 1 && <ChevronRight className={cn("h-4 w-4", i < sc.stage ? "text-primary" : "text-muted-foreground/50")} />}
              </div>
            );
          })}
        </div>
      </Panel>

      <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
        <LiveMetric label="Grid Health" value={`${sc.gridHealth}%`} tone={healthTone} />
        <LiveMetric label="Network Latency" value={`${sc.latency} ms`} tone={latTone} />
        <LiveMetric label="Threat Confidence" value={`${sc.confidence}%`} tone={confTone} />
        <LiveMetric label="Risk Score" value={`${sc.risk}/100`} tone={riskTone} />
      </div>
    </div>
  );
}

function LiveMetric({ label, value, tone }: { label: string; value: string; tone: Status }) {
  return (
    <div className="rounded-lg border bg-card p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">{label}</span>
        <Dot status={tone} />
      </div>
      <div className={cn("mt-3 text-3xl font-semibold tabular-nums", toneText[tone])}>{value}</div>
    </div>
  );
}
