import { createFileRoute } from "@tanstack/react-router";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, PieChart, Pie, Cell } from "recharts";
import { Dot, Metric, Panel, PageHeading, riskTone, toneText } from "@/components/soc";
import { commandMetrics, gridPerformance, gridStatus, recentEvents, securityOverview } from "@/data/mock";
import { useSimulation } from "@/lib/simulation";
import { getRiskSeverity } from "@/lib/risk";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { title: "Command Center — GridNexus AI" },
      { name: "description", content: "Live smart grid health, security status and risk overview." },
      { property: "og:title", content: "Command Center — GridNexus AI" },
      { property: "og:description", content: "Live smart grid health, security status and risk overview." },
    ],
  }),
  component: CommandCenter,
});

const tooltipStyle = { background: "var(--popover)", border: "1px solid var(--border)", borderRadius: 6, fontSize: 12 };

function CommandCenter() {
  const { result, attack, target, alertsList } = useSimulation();
  const active = result.detection !== null;
  const latest = alertsList[0];
  const data = {
    gridHealth: result.gridHealth,
    securityStatus: active ? "Threat Detected" : "Secure",
    connectedDevices: commandMetrics.connectedDevices,
    activeThreats: active ? 1 : 0,
    overallRisk: result.detection?.risk ?? commandMetrics.riskScore,
    securityOverview: { ...securityOverview, suspicious: securityOverview.suspicious + (active ? 1 : 0), critical: result.detection?.severity === "CRITICAL" ? 1 : 0 },
    recentEvents: active ? [{ id: 2, text: `${result.detection?.type} detected on ${target}`, time: result.detection?.time ?? "" }, ...recentEvents.slice(0, 4)] : recentEvents,
    gridStatus,
    gridPerformance: gridPerformance.map((point, index) => active && index >= 20 ? { ...point, voltage: attack === "fdi" ? 254 : point.voltage, frequency: attack === "fdi" ? 50.62 : point.frequency, load: attack === "fdi" ? 207 : point.load } : point),
    activeAttack: attack,
  };

  const isSecure = data.securityStatus === "Secure";
  const donut = [
    { name: "Normal", value: data.securityOverview.normal, color: "var(--safe)" },
    { name: "Suspicious", value: data.securityOverview.suspicious, color: "var(--warn)" },
    { name: "Critical", value: data.securityOverview.critical, color: "var(--critical)" },
  ];

  const riskLabel =
    getRiskSeverity(data.overallRisk);

  return (
    <div className="space-y-6">
      <PageHeading title="Command Center" subtitle="Smart grid operations and security overview" />
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-5">
        <Metric
          label="Grid Health"
          value={`${data.gridHealth}%`}
          sub={
            <span className={data.gridHealth >= 90 ? "text-safe" : data.gridHealth >= 80 ? "text-warn" : "text-critical"}>
              Status: {data.gridHealth >= 90 ? "Stable" : "Degraded"}
            </span>
          }
        />
        <Metric
          label="Security Status"
          value={
            <span className={`flex items-center gap-2 ${isSecure ? "text-safe" : "text-critical"}`}>
              <Dot status={isSecure ? "normal" : "threat"} />
              {data.securityStatus}
            </span>
          }
          sub={isSecure ? "All controls active" : "Active mitigation required"}
        />
        <Metric label="Connected Devices" value={data.connectedDevices} sub="All reporting" />
        <Metric
          label="Active Threats"
          value={data.activeThreats}
          tone={data.activeThreats > 0 ? "threat" : undefined}
          sub="Last 24h"
        />
        <Metric
          label="Overall Risk"
          value={<span className={toneText[riskTone(data.overallRisk)]}>{riskLabel}</span>}
          sub={`${data.overallRisk}/100`}
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <Panel title="Live Grid Performance" className="xl:col-span-2">
          <div className="h-72">
            <ResponsiveContainer>
              <LineChart data={data.gridPerformance} margin={{ left: -10, right: 4 }}>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="time" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} interval={3} />
                <YAxis yAxisId="v" domain={[210, 260]} stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis yAxisId="l" orientation="right" domain={[80, 220]} stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis yAxisId="f" hide domain={[49.5, 50.8]} />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend iconType="plainline" wrapperStyle={{ fontSize: 12 }} />
                <Line yAxisId="v" dataKey="voltage" name="Voltage (V)" stroke="var(--chart-1)" dot={false} strokeWidth={2} />
                <Line yAxisId="f" dataKey="frequency" name="Frequency (Hz)" stroke="var(--chart-2)" dot={false} strokeWidth={1.5} />
                <Line yAxisId="l" dataKey="load" name="Power Load (MW)" stroke="var(--chart-3)" dot={false} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Security Monitoring">
          <div className="space-y-2">
            {[
              ["Normal Events", data.securityOverview.normal.toLocaleString(), "normal"],
              ["Suspicious Events", data.securityOverview.suspicious, "warning"],
              ["Critical Threats", data.securityOverview.critical, data.securityOverview.critical > 0 ? "threat" : "offline"],
            ].map(([l, v, s]) => (
              <div key={l as string} className="flex items-center justify-between rounded-md border bg-background/40 px-3 py-2.5">
                <span className="flex items-center gap-2 text-sm text-muted-foreground"><Dot status={s as "normal"} />{l}</span>
                <span className="font-semibold tabular-nums">{v}</span>
              </div>
            ))}
          </div>
          <div className="mt-5 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Current Security Status</div>
          <div className="relative mx-auto h-40 w-40">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={donut} dataKey="value" innerRadius={52} outerRadius={64} stroke="none" startAngle={90} endAngle={-270}>
                  {donut.map((d) => <Cell key={d.name} fill={d.color} />)}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className={`absolute inset-0 flex items-center justify-center text-sm font-bold tracking-widest ${isSecure ? "text-safe" : "text-critical"}`}>
              {isSecure ? "SECURE" : "ALERT"}
            </div>
          </div>
        </Panel>
      </div>

      {latest && <Panel title="Latest Detection">
        <dl className="grid grid-cols-2 gap-4 md:grid-cols-4 text-sm">
          {[["Device ID", latest.device], ["Threat Type", latest.type], ["Confidence", `${latest.confidence}%`], ["Risk Score", `${latest.risk}/100 · ${getRiskSeverity(latest.risk)}`]].map(([label, value]) => <div key={label}><dt className="text-[11px] uppercase text-muted-foreground">{label}</dt><dd className={`mt-1 font-medium ${label === "Risk Score" ? toneText[riskTone(latest.risk)] : ""}`}>{value}</dd></div>)}
        </dl>
      </Panel>}

      <div className="grid gap-6 xl:grid-cols-2">
        <Panel title="Recent Security Events">
          <ul className="divide-y">
            {data.recentEvents.map((e) => (
              <li key={e.id} className="flex items-center justify-between py-2.5 text-sm">
                <span className="flex items-center gap-3">
                  <Dot status={data.activeAttack !== "normal" && e.id === 2 ? "threat" : "normal"} />
                  {e.text}
                </span>
                <span className="font-mono text-xs text-muted-foreground">{e.time}</span>
              </li>
            ))}
          </ul>
        </Panel>
        <Panel title="Grid Status">
          <ul className="divide-y">
            {data.gridStatus.map((d) => (
              <li key={d} className="flex items-center justify-between py-2.5 text-sm">
                <span>{d}</span>
                <span className={`flex items-center gap-2 text-xs ${active && (d === "Smart Meter Cluster" && target?.startsWith("SM-") || d === "Feeder A" && target === "FDR-A" || d === "Feeder B" && target === "FDR-B") ? "text-warn" : "text-safe"}`}><Dot status={active && (d === "Smart Meter Cluster" && target?.startsWith("SM-") || d === "Feeder A" && target === "FDR-A" || d === "Feeder B" && target === "FDR-B") ? "warning" : "normal"} />{active && (d === "Smart Meter Cluster" && target?.startsWith("SM-") || d === "Feeder A" && target === "FDR-A" || d === "Feeder B" && target === "FDR-B") ? "Warning" : "Operational"}</span>
              </li>
            ))}
          </ul>
        </Panel>
      </div>
    </div>
  );
}
