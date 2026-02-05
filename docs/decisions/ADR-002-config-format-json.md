# ADR-002: Application Configuration Format

## Status
Accepted

## Context
The application requires a persistent configuration system to store user preferences, classification rules, and UI state.

## Decision
JSON (`.json`) was selected as the primary configuration format.

## Alternatives Considered
- **YAML**:
  - Pros: Human readable, supports comments.
  - Cons: Requires an external library (`pyyaml`).
- **INI/Conf**:
  - Pros: Built-in Python support (`configparser`).
  - Cons: Limited support for nested structures (like our complex category mappings).

## Rationale
JSON provides a native, zero-dependency storage format that handles nested dictionaries and lists effortlessly. It is standard for modern applications and easily human-editable.

## Consequences
- **Benefits**: No extra dependencies needed, direct mapping to Python dictionaries, easy serialization.
- **Limitations**: Does not natively support comments (handled by keeping a separate manual or well-documented defaults).
