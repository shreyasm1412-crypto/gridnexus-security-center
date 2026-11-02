import { Link, useRouterState } from "@tanstack/react-router";
import { useEffect, useState, type ReactNode } from "react";
import { Bell, LayoutDashboard, Network, ShieldAlert, FlaskConical, ClipboardList, User } from "lucide-react";
import { Dot } from "./soc";
import { cn } from "@/lib/utils";

const nav = [
  { to: "/", label: "Command Center", icon: LayoutDashboard },
  { to: "/topology", label: "Grid Topology", icon: Network },
  { to: "/threats", label: "Threat Detection", icon: ShieldAlert },
  { to: "/simulation", label: "Attack Simulation", icon: FlaskConical },
  { to: "/incidents", label: "Incident Management", icon: ClipboardList },
] as const;

function Clock() {
  const [now, setNow] = useState<Date | null>(null);
  useEffect(() => {
    setNow(new Date());
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return <span className="font-mono text-sm tabular-nums text-muted-foreground">{now ? now.toLocaleTimeString([], { hour12: false }) : "--:--:--"}</span>;
}

export function AppShell({ children }: { children: ReactNode }) {
  const path = useRouterState({ select: (s) => s.location.pathname });
  const current = nav.find((n) => n.to === path) ?? nav[0];

  return (
    <div className="flex min-h-screen w-full">
      <aside className="sticky top-0 flex h-screen w-16 shrink-0 flex-col border-r bg-sidebar lg:w-60">
        <div className="border-b border-sidebar-border px-4 py-5">
          <div className="text-lg font-bold tracking-tight text-sidebar-foreground">
            <span className="text-energy">⚡</span><span className="hidden lg:inline"> GridNexus AI</span>
          </div>
          <div className="mt-0.5 hidden text-xs text-muted-foreground lg:block">Smart Grid Cyber Defense</div>
        </div>
        <nav className="flex-1 space-y-1 p-2">
          {nav.map((n) => {
            const active = n.to === path;
            return (
              <Link
                key={n.to}
                to={n.to}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                  active ? "bg-sidebar-accent text-sidebar-accent-foreground" : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-sidebar-foreground",
                )}
              >
                <n.icon className={cn("h-4 w-4 shrink-0", active && "text-primary")} />
                <span className="hidden lg:inline">{n.label}</span>
              </Link>
            );
          })}
        </nav>
        <div className="flex items-center gap-2 border-t border-sidebar-border px-5 py-4 text-xs font-semibold tracking-wider text-safe">
          <Dot status="normal" /> <span className="hidden lg:inline">SYSTEM ONLINE</span>
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-10 flex h-14 items-center justify-between border-b bg-background/90 px-6 backdrop-blur">
          <div className="text-sm font-medium">{current.label}</div>
          <div className="flex items-center gap-5">
            <span className="flex items-center gap-2 rounded-full border border-energy/30 px-3 py-1 text-[11px] font-semibold tracking-wider text-energy">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-energy" /> LIVE SIMULATION
            </span>
            <Clock />
            <button aria-label="Notifications" className="text-muted-foreground hover:text-foreground"><Bell className="h-4 w-4" /></button>
            <div className="flex h-7 w-7 items-center justify-center rounded-full border bg-secondary"><User className="h-3.5 w-3.5 text-muted-foreground" /></div>
          </div>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
