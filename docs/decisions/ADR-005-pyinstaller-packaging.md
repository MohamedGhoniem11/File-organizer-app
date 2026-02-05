# ADR-005: PyInstaller for Executable Packaging

## Status
Accepted

## Context
The application needs to be distributed as a standalone Windows executable to ensure users can run it without having a Python environment pre-installed.

## Decision
PyInstaller was selected for generating standalone binaries.

## Alternatives Considered
- **Nuitka**:
  - Pros: Compiles to C for speed and better obfuscation.
  - Cons: Slower build times, can be brittle with complex GUI dependencies like `customtkinter`.
- **cx_Freeze**:
  - Pros: Mature.
  - Cons: Configuration is often more verbose than PyInstaller's simple CLI.

## Rationale
PyInstaller is the industry-standard for Python packaging. It handles complex dependency trees automatically and supports a single-file (`--onefile`) output which is ideal for a portable utility application.

## Consequences
- **Benefits**: Simple distribution, single-file executable, handles `customtkinter` assets well.
- **Limitations**: Large file size (includes Python interpreter); often triggers false positives in Antivirus software.
