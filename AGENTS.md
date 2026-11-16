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
- Simulation state, detection history, device telemetry, and incident history are shared via src/lib/simulation.tsx using the FastAPI snapshot adapter; mock simulation remains available only when no API is configured.
- The existing Python FastAPI service owns simulation inference and transactional SQLite persistence; host it externally for published deployments because the frontend host cannot run Python.
- Derive all risk labels, colors, and severity badges from src/lib/risk.ts to prevent inconsistent score boundaries.
