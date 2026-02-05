# ADR-003: GUI Toolkit Choice

## Status
Accepted

## Context
A user-friendly dashboard is required to provide status updates, configuration editing, and manual tool triggers.

## Decision
`customtkinter` was selected as the GUI toolkit.

## Alternatives Considered
- **Standard Tkinter**:
  - Pros: Built into Python.
  - Cons: Outdated aesthetics, lacks modern dark mode support.
- **PyQt/PySide**:
  - Pros: Extremely powerful, enterprise-grade.
  - Cons: Large footprint, complex licensing (GPL/LGPL), steep learning curve for simple dashboards.

## Rationale
`customtkinter` provides a modern, "premium" look and feel built directly on top of standard Tkinter. It offers built-in Dark Mode support and high-DPI scaling while maintaining a lightweight footprint.

## Consequences
- **Benefits**: Beautiful modern UI, relatively simple API, dark/light mode support.
- **Limitations**: External dependency; some standard Tkinter widgets require custom wrappers for aesthetic consistency.
