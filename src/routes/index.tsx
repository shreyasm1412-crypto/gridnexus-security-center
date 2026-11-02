import { createFileRoute } from "@tanstack/react-router";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, PieChart, Pie, Cell } from "recharts";
import { Dot, Metric, Panel, PageHeading } from "@/components/soc";
import { commandMetrics, gridPerformance, gridStatus, recentEvents, securityOverview } from "@/data/mock";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
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
  const donut = [
    { name: "Normal", value: securityOverview.normal, color: "var(--safe)" },
    { name: "Suspicious", value: securityOverview.suspicious * 40, color: "var(--warn)" },
  ];
  return (
    <div className="space-y-6">
      <PageHeading title="Command Center" subtitle="Smart grid operations and security overview" />
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-5">
        <Metric label="Grid Health" value={`${commandMetrics.gridHealth}%`} sub={<span className="text-safe">Status: Stable</span>} />
        <Metric label="Security Status" value={<span className="flex items-center gap-2 text-safe"><Dot status="normal" />Secure</span>} sub="All controls active" />
        <Metric label="Connected Devices" value={commandMetrics.connectedDevices} sub="All reporting" />
        <Metric label="Active Threats" value={commandMetrics.activeThreats} sub="Last 24h" />
        <Metric label="Overall Risk" value={<span className="text-safe">Low</span>} sub={`${commandMetrics.riskScore}/100`} />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <Panel title="Live Grid Performance" className="xl:col-span-2">
          <div className="h-72">
            <ResponsiveContainer>
              <LineChart data={gridPerformance} margin={{ left: -10, right: 4 }}>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="time" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} interval={3} />
                <YAxis yAxisId="v" domain={[220, 240]} stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis yAxisId="l" orientation="right" domain={[80, 200]} stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis yAxisId="f" hide domain={[49.8, 50.2]} />
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
              ["Normal Events", securityOverview.normal.toLocaleString(), "normal"],
              ["Suspicious Events", securityOverview.suspicious, "warning"],
              ["Critical Threats", securityOverview.critical, "offline"],
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
            <div className="absolute inset-0 flex items-center justify-center text-sm font-bold tracking-widest text-safe">SECURE</div>
          </div>
        </Panel>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Panel title="Recent Security Events">
          <ul className="divide-y">
            {recentEvents.map((e) => (
              <li key={e.id} className="flex items-center justify-between py-2.5 text-sm">
                <span className="flex items-center gap-3"><Dot status="normal" />{e.text}</span>
                <span className="font-mono text-xs text-muted-foreground">{e.time}</span>
              </li>
            ))}
          </ul>
        </Panel>
        <Panel title="Grid Status">
          <ul className="divide-y">
            {gridStatus.map((d) => (
              <li key={d} className="flex items-center justify-between py-2.5 text-sm">
                <span>{d}</span>
                <span className="flex items-center gap-2 text-xs text-safe"><Dot status="normal" />Operational</span>
              </li>
            ))}
          </ul>
        </Panel>
      </div>
    </div>
  );
}
