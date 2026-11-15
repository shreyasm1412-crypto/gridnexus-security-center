import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Activity, Database, ServerCrash, KeyRound, RotateCcw, ChevronRight, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dot, PageHeading, Panel, toneText, riskTone } from "@/components/soc";
import { attackScenarios, simulationStages, simulationTargets, type AttackKey, type Status } from "@/data/mock";
import { useSimulation } from "@/lib/simulation";
import { getRiskSeverity, type RiskTone } from "@/lib/risk";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/simulation")({
  head: () => ({ meta: [
    { title: "Attack Simulation — GridNexus AI" },
    { name: "description", content: "Controlled cyberattack simulation lab for smart grid security testing." },
    { property: "og:title", content: "Attack Simulation — GridNexus AI" },
    { property: "og:description", content: "Controlled cyberattack simulation lab for smart grid security testing." },
    { property: "og:type", content: "website" },
    { name: "twitter:card", content: "summary_large_image" },
  ] }),
  component: Simulation,
});

const cards: { key: AttackKey; icon: typeof Activity }[] = [
  { key: "normal", icon: Activity }, { key: "fdi", icon: Database },
  { key: "dos", icon: ServerCrash }, { key: "ua", icon: KeyRound },
];

function Simulation() {
  const { attack, result, startSimulation, resetSimulation } = useSimulation();
  const [selectedAttack, setSelectedAttack] = useState<AttackKey>(attack);
  const [deviceId, setDeviceId] = useState(result.request.deviceId);
  const scenario = attackScenarios[attack];
  const isNormal = attack === "normal";
  const currentStage = isNormal ? 0 : simulationStages.length - 1;
  const { telemetry, gridHealth } = result;
  const confidence = result.detection?.confidence ?? 0;
  const risk = result.detection?.risk ?? attackScenarios.normal.risk;
  const reset = () => { resetSimulation(); setSelectedAttack("normal"); };
  const healthTone: Status = gridHealth >= 90 ? "normal" : gridHealth >= 80 ? "warning" : "threat";
  const latencyTone: Status = telemetry.latency < 30 ? "normal" : telemetry.latency < 100 ? "warning" : "threat";

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <PageHeading title="Cyberattack Simulation Lab" subtitle="Controlled Smart Grid Security Testing Environment" />
        <span className="rounded border border-warn/40 bg-warn/10 px-3 py-1.5 text-[11px] font-semibold tracking-wider text-warn">SIMULATION ONLY — NO REAL GRID SYSTEMS ARE CONNECTED</span>
      </div>
      <Panel>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Current Simulation Status</div>
            <div aria-live="polite" className={cn("mt-1 flex items-center gap-3 text-xl font-bold tracking-wide", isNormal ? "text-safe" : "text-critical")}>
              <Dot status={isNormal ? "normal" : "threat"} className="h-3 w-3" />
              {isNormal ? "NORMAL OPERATION" : `${scenario.title.toUpperCase()} IN PROGRESS`}
            </div>
            {!isNormal && <div className="mt-1 text-xs text-muted-foreground">Target device: <span className="font-mono">{result.request.deviceId}</span></div>}
          </div>
          <Button variant="outline" onClick={reset} disabled={isNormal}><RotateCcw />RESET TO NORMAL</Button>
        </div>
      </Panel>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {cards.map(({ key, icon: Icon }) => (
          <Button key={key} variant="outline" aria-pressed={selectedAttack === key} onClick={() => setSelectedAttack(key)} className={cn(
            "h-auto whitespace-normal rounded-lg border bg-card p-5 text-left shadow-sm transition-colors hover:border-primary/60 flex-col items-start gap-0",
            selectedAttack === key && (key === "normal" ? "border-safe/70 bg-safe/5" : "border-critical/70 bg-critical/5"),
          )}>
            <Icon className={cn("h-5 w-5", selectedAttack === key ? key === "normal" ? "text-safe" : "text-critical" : "text-energy")} />
            <span className="mt-3 text-sm font-semibold tracking-wide">{attackScenarios[key].title.toUpperCase()}</span>
            <span className="mt-1 text-xs font-normal leading-relaxed text-muted-foreground">{attackScenarios[key].description}</span>
          </Button>
        ))}
      </div>
      <Panel title="Simulation Controls">
        <div className="grid items-end gap-4 sm:grid-cols-2 xl:grid-cols-[1fr_1fr_auto]">
          <div><label htmlFor="target-device" className="mb-2 block text-xs text-muted-foreground">Select Target Device</label>
            <Select value={deviceId} onValueChange={setDeviceId}><SelectTrigger id="target-device"><SelectValue /></SelectTrigger><SelectContent>{simulationTargets.map((id) => <SelectItem key={id} value={id}>{id}</SelectItem>)}</SelectContent></Select>
          </div>
          <div><label htmlFor="attack-type" className="mb-2 block text-xs text-muted-foreground">Select Attack Type</label>
            <Select value={selectedAttack} onValueChange={(value) => { const option = cards.find((card) => card.key === value); if (option) setSelectedAttack(option.key); }}><SelectTrigger id="attack-type"><SelectValue /></SelectTrigger><SelectContent>{cards.map(({ key }) => <SelectItem key={key} value={key}>{attackScenarios[key].title}</SelectItem>)}</SelectContent></Select>
          </div>
          <Button onClick={() => startSimulation({ deviceId, attack: selectedAttack })}><Play />START SIMULATION</Button>
        </div>
      </Panel>
      <Panel title="Simulation Flow">
        <div className="flex flex-wrap items-center gap-2" aria-live="polite">
          {simulationStages.map((stage, index) => (
            <div key={stage} className="flex items-center gap-2">
              <div aria-current={index === currentStage ? "step" : undefined} className={cn("rounded-md border px-3 py-2 text-[11px] font-semibold tracking-wider",
                index === currentStage && (isNormal ? "border-safe bg-safe/10 text-safe" : "border-critical bg-critical/10 text-critical"),
                index < currentStage && "border-primary/50 bg-primary/10 text-primary", index > currentStage && "text-muted-foreground",
              )}>{stage.toUpperCase()}</div>
              {index < simulationStages.length - 1 && <ChevronRight className={cn("h-4 w-4", index < currentStage ? "text-primary" : "text-muted-foreground/50")} />}
            </div>
          ))}
        </div>
      </Panel>
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
        <LiveMetric label="Grid Health" value={`${gridHealth}%`} tone={healthTone} />
        <LiveMetric label="Network Latency" value={`${telemetry.latency} ms`} tone={latencyTone} />
        <LiveMetric label="Threat Confidence" value={`${confidence}%`} tone={isNormal ? "normal" : "warning"} />
        <LiveMetric label="Risk Score" value={`${risk}/100`} tone={riskTone(risk)} sub={getRiskSeverity(risk)} />
      </div>
      <Panel title="Live Telemetry" action={<span className="font-mono text-xs text-muted-foreground">{result.request.deviceId}</span>}>
        <div className="grid gap-6 md:grid-cols-2">
          <TelemetryGroup title="Electrical Telemetry" rows={[["Voltage", telemetry.voltage], ["Current", telemetry.current], ["Frequency", telemetry.frequency], ["Power", telemetry.power]]} tone={attack === "fdi" ? "warning" : "normal"} />
          <TelemetryGroup title="Network Telemetry" rows={[["Network Latency", `${telemetry.latency} ms`], ["Packet Rate", `${telemetry.packetRate} pkts/s`], ["Packet Loss", `${telemetry.packetLoss}%`], ["Failed Login Attempts", String(telemetry.failedLogins)]]} tone={attack === "dos" || attack === "ua" ? "warning" : "normal"} />
        </div>
      </Panel>
    </div>
  );
}

function LiveMetric({ label, value, tone, sub }: { label: string; value: string; tone: RiskTone; sub?: string }) {
  return <div className="rounded-lg border bg-card p-5 shadow-sm"><div className="flex items-center justify-between gap-2"><span className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">{label}</span><Dot status={tone === "high" ? "warning" : tone} /></div><div className={cn("mt-3 text-3xl font-semibold tabular-nums", toneText[tone])}>{value}</div>{sub && <div className={cn("mt-1 text-xs font-semibold", toneText[tone])}>{sub}</div>}</div>;
}

function TelemetryGroup({ title, rows, tone }: { title: string; rows: [string, string][]; tone: Status }) {
  return <div><h3 className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">{title}</h3><dl className="divide-y">{rows.map(([label, value]) => <div key={label} className="flex justify-between gap-4 py-2.5 text-sm"><dt className="text-muted-foreground">{label}</dt><dd className={cn("font-mono text-right tabular-nums", toneText[tone])}>{value}</dd></div>)}</dl></div>;
}
