# Requested updates
- [x] Preserve the five pages and existing dashboard styling.
- [x] Add typed shared mock simulation data and consistent risk scoring.
- [x] Add target/attack controls, live telemetry, and the demonstration flow.
- [x] Connect latest detection, topology details, explanations, and incidents to shared simulation results.
- [x] Verify risk boundaries and the cross-page simulation flow on desktop and mobile.

Verification: 12 tests passed; selected-device FDI appears across all five pages; DoS, unauthorized access, incident status changes, and reset verified with no runtime errors or backend requests. Updated controls and telemetry fit a 390px screen. The unchanged top header has pre-existing horizontal overflow on that screen; left untouched to preserve the requested layout.