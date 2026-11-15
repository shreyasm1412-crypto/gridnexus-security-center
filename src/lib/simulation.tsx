import { createContext, useContext, useState, type ReactNode } from "react";
import { alerts, incidents, type Incident, type SimulationRequest, type SimulationResult } from "@/data/mock";
import { simulateTelemetry } from "@/lib/simulation-model";

function initialState() {
  return { result: simulateTelemetry({ deviceId: "SM-04", attack: "normal" }, 0, ""), alertsList: alerts, incidentsList: incidents, runId: 0 };
}

type SimulationContextType = {
  attack: SimulationRequest["attack"];
  target: string | null;
  result: SimulationResult;
  alertsList: typeof alerts;
  incidentsList: typeof incidents;
  startSimulation: (request: SimulationRequest) => void;
  resetSimulation: () => void;
  updateStatus: (id: string, status: Incident["status"]) => void;
};

const Ctx = createContext<SimulationContextType | null>(null);

export function SimulationProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState(initialState);
  const startSimulation = (request: SimulationRequest) => {
    const timestamp = new Date().toISOString();
    setState((previous) => {
      const runId = previous.runId + 1;
      const result = simulateTelemetry(request, runId, timestamp);
      return { result, runId,
        alertsList: result.detection ? [result.detection, ...previous.alertsList] : previous.alertsList,
        incidentsList: result.incident ? [result.incident, ...previous.incidentsList] : previous.incidentsList,
      };
    });
  };
  const resetSimulation = () => setState((previous) => ({ ...previous, result: simulateTelemetry({ ...previous.result.request, attack: "normal" }, previous.runId, "") }));
  const updateStatus = (id: string, status: Incident["status"]) => setState((previous) => ({ ...previous,
    incidentsList: previous.incidentsList.map((incident) => incident.id === id ? { ...incident, status } : incident),
  }));
  return <Ctx.Provider value={{ attack: state.result.request.attack, target: state.result.detection ? state.result.request.deviceId : null,
    result: state.result, alertsList: state.alertsList, incidentsList: state.incidentsList, startSimulation, resetSimulation, updateStatus }}>{children}</Ctx.Provider>;
}

export function useSimulation() {
  const context = useContext(Ctx);
  if (!context) throw new Error("SimulationProvider is required");
  return context;
}
