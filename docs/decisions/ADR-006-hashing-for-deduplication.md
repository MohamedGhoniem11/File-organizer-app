# ADR-006: File Hashing for Deduplication

## Status
Accepted

## Context
A key feature of the Health Engine is identifying identical files to reclaim disk space. Filenames are unreliable indicators of identity.

## Decision
SHA-256 hashing (`hashlib.sha256`) was selected for file content comparison.

## Alternatives Considered
- **Filename/Size Comparison**:
  - Pros: Instant.
  - Cons: Extremely inaccurate; different files can have same names, and same files can have different names.
- **MD5 Hashing**:
  - Pros: Faster than SHA-256.
  - Cons: Susceptible to collisions (though rare in this context, modern standard favors SHA).

## Rationale
SHA-256 provides a practically collision-free way to verify that two files are identical. By hashing the content, we ensure that files are only deleted if they are byte-for-byte duplicates.

## Consequences
- **Benefits**: Extremely high accuracy for deduplication.
- **Limitations**: Reading large files to calculate hashes can be I/O intensive; mitigated by only hashing files when strictly necessary (e.g., during a Health Audit).
