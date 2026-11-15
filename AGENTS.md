<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->

## Architecture
- All mock data lives in src/data/mock.ts with API-shaped types so it can be swapped for FastAPI calls without touching UI.
- Simulation state, detection history, and incident history are shared via src/lib/simulation.tsx; use typed SimulationRequest/SimulationResult and the pure mock adapter so all five pages reflect the same run without network calls.
- Derive all risk labels, colors, and severity badges from src/lib/risk.ts to prevent inconsistent score boundaries.
