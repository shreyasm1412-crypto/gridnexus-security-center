import { createContext, useContext, useState, type ReactNode } from "react";
import type { AttackKey } from "@/data/mock";

const Ctx = createContext<{ attack: AttackKey; setAttack: (a: AttackKey) => void }>({
  attack: "normal",
  setAttack: () => {},
});

export function SimulationProvider({ children }: { children: ReactNode }) {
  const [attack, setAttack] = useState<AttackKey>("normal");
  return <Ctx.Provider value={{ attack, setAttack }}>{children}</Ctx.Provider>;
}

export const useSimulation = () => useContext(Ctx);
