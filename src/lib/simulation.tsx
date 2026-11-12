import { createContext, useContext, useState, type ReactNode } from "react";
import type { AttackKey } from "@/data/mock";
import { triggerSimulation } from "./api";

type SimulationContextType = {
  attack: AttackKey;
  setAttack: (a: AttackKey) => void;
  simData: any | null;
};

const Ctx = createContext<SimulationContextType>({
  attack: "normal",
  setAttack: () => {},
  simData: null,
});

export function SimulationProvider({ children }: { children: ReactNode }) {
  const [attack, setAttackState] = useState<AttackKey>("normal");
  const [simData, setSimData] = useState<any | null>(null);

  const setAttack = (newAttack: AttackKey) => {
    setAttackState(newAttack);
    triggerSimulation(newAttack)
      .then((res) => {
        if (res) setSimData(res);
      })
      .catch((err) => {
        console.warn("Backend simulation trigger failed (using offline mode):", err);
      });
  };

  return <Ctx.Provider value={{ attack, setAttack, simData }}>{children}</Ctx.Provider>;
}

export const useSimulation = () => useContext(Ctx);
