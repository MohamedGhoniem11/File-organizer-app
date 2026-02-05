# ADR-001: Selection of File Monitoring Library

## Status
Accepted

## Context
The application requires real-time monitoring of a specific directory to trigger organizational logic as soon as files are created or moved.

## Decision
The `watchdog` library was selected for file system event monitoring.

## Alternatives Considered
- **Polling (`os.listdir`)**:
  - Pros: No external dependencies.
  - Cons: High resource usage, inefficient for large directories, delayed response.
- **`shutil` built-ins**: Not applicable for real-time monitoring.

## Rationale
`watchdog` is a cross-platform, mature library that utilizes native OS event APIs (like `inotify` on Linux or `ReadDirectoryChangesW` on Windows) for highly efficient, near-instantaneous notification of file events with minimal CPU overhead.

## Consequences
- **Benefits**: Native performance, high responsiveness, easy implementation of event handlers.
- **Limitations**: Adds an external dependency; requires handling of event "noise" (e.g., partial writes).
