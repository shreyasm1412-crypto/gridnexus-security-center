import { Link, useRouterState } from "@tanstack/react-router";
import { useEffect, useState, type ReactNode } from "react";
import {
  Bell,
  LayoutDashboard,
  Network,
  ShieldAlert,
  FlaskConical,
  ClipboardList,
  User,
  UserRound,
  Activity,
  LogOut,
} from "lucide-react";
import { Dot } from "./soc";
import { cn } from "@/lib/utils";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { notifications, systemStatus } from "@/data/mock";

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

function NotificationsMenu() {
  const [open, setOpen] = useState(false);
  const [readIds, setReadIds] = useState<string[]>([]);
  const unread = notifications.filter((n) => !readIds.includes(n.id)).length;

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          aria-label="Notifications"
          className="relative cursor-pointer rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
        >
          <Bell className="h-4 w-4" />
          {unread > 0 && <span className="absolute right-1 top-1 h-1.5 w-1.5 rounded-full bg-energy" />}
        </button>
      </PopoverTrigger>
      <PopoverContent align="end" sideOffset={8} className="w-80 max-w-[calc(100vw-1.5rem)] p-0">
        <div className="flex items-center justify-between border-b px-4 py-3">
          <span className="text-sm font-semibold">Notifications</span>
          <button
            onClick={() => setReadIds(notifications.map((n) => n.id))}
            className="cursor-pointer text-[11px] font-medium text-energy transition-opacity hover:opacity-80"
          >
            Mark all as read
          </button>
        </div>
        <ul className="max-h-72 overflow-y-auto">
          {notifications.map((n) => (
            <li key={n.id} className="flex gap-3 border-b px-4 py-3 last:border-0">
              <Dot status={n.status} className="mt-1.5" />
              <div className="min-w-0">
                <div className="text-sm font-medium leading-snug">{n.title}</div>
                <div className="text-xs text-muted-foreground">{n.detail}</div>
                <div className="mt-1 text-[11px] text-muted-foreground">{n.time}</div>
              </div>
            </li>
          ))}
        </ul>
      </PopoverContent>
    </Popover>
  );
}

function MenuItem({ icon: Icon, label, onClick }: { icon: typeof User; label: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="flex w-full cursor-pointer items-center gap-2.5 rounded-md px-2 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
    >
      <Icon className="h-3.5 w-3.5" />
      {label}
    </button>
  );
}

function ProfileMenu() {
  const [open, setOpen] = useState(false);
  const [statusOpen, setStatusOpen] = useState(false);
  const [signOutOpen, setSignOutOpen] = useState(false);

  const openStatus = () => {
    setOpen(false);
    setStatusOpen(true);
  };

  const openSignOut = () => {
    setOpen(false);
    setSignOutOpen(true);
  };

  return (
    <>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <button
            aria-label="Profile"
            className="flex h-7 w-7 cursor-pointer items-center justify-center rounded-full border bg-secondary transition-colors hover:border-primary/50 hover:bg-accent"
          >
            <User className="h-3.5 w-3.5 text-muted-foreground" />
          </button>
        </PopoverTrigger>
        <PopoverContent align="end" sideOffset={8} className="w-64 max-w-[calc(100vw-1.5rem)] p-2">
          <div className="border-b px-2 pb-3 pt-1">
            <div className="text-sm font-semibold">Grid Administrator</div>
            <div className="mt-0.5 text-xs text-muted-foreground">Role: Security Operations Admin</div>
          </div>
          <div className="mt-1.5 space-y-0.5">
            <MenuItem icon={UserRound} label="Profile" onClick={() => setOpen(false)} />
            <MenuItem icon={Activity} label="System Status" onClick={openStatus} />
            <MenuItem icon={LogOut} label="Sign Out" onClick={openSignOut} />
          </div>
        </PopoverContent>
      </Popover>

      <Dialog open={statusOpen} onOpenChange={setStatusOpen}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>System Status</DialogTitle>
            <DialogDescription>Current simulated grid and monitoring state.</DialogDescription>
          </DialogHeader>
          <dl className="space-y-2 text-sm">
            {systemStatus.map((row) => (
              <div key={row.label} className="flex items-center justify-between rounded-md border px-3 py-2">
                <dt className="text-muted-foreground">{row.label}</dt>
                <dd className="flex items-center gap-2 font-medium">
                  <Dot status={row.status} />
                  {row.value}
                </dd>
              </div>
            ))}
          </dl>
        </DialogContent>
      </Dialog>

      <Dialog open={signOutOpen} onOpenChange={setSignOutOpen}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Sign Out</DialogTitle>
            <DialogDescription>Are you sure you want to sign out of GridNexus AI?</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <button
              onClick={() => setSignOutOpen(false)}
              className="cursor-pointer rounded-md border border-input px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
            >
              Cancel
            </button>
            <button
              onClick={() => setSignOutOpen(false)}
              className="cursor-pointer rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              Sign Out
            </button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
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
            <NotificationsMenu />
            <ProfileMenu />
          </div>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
