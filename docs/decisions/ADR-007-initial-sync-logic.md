# ADR-007: Initial Sync Logic on Startup

## Status
Accepted

## Context
By default, the `watchdog` library only monitors for *new* filesystem events. Files already present in the directory when the app starts are ignored until moved or touched.

## Decision
Implement a proactive "Initial Sync" scan that runs once at service startup.

## Alternatives Considered
- **Event-Only Monitoring**:
  - Pros: Simpler code.
  - Cons: Poor UX; users expect their existing mess to be cleaned up as soon as they start the tool.
- **Full Refresh on Periodical Schedule**:
  - Pros: More robust.
  - Cons: Redundant with real-time monitoring.

## Rationale
Initial Sync provides immediate value to the user. By iterating through existing files exactly once at startup, we reconcile the current state of the filesystem with our classification rules.

## Consequences
- **Benefits**: High user satisfaction, immediate organizational results.
- **Limitations**: Startup time may be slightly increased if the watched folder contains thousands of files.
