# ADR-009: NLP Reliability and Fallback Strategy

## Status
Accepted

## Context
The Intelligent Assistant relies on the `spaCy` NLP model for entity extraction and intent detection. However, language models are large dependencies that may be missing, fail to load, or be unavailable in certain environments (e.g., offline or restricted EXE execution).

## Decision
Implement a layered reliability strategy:
1. **Auto-Discovery**: Verify model presence on startup.
2. **Auto-Download**: Attempt to retrieve missing models via `spacy.cli` if internet is available.
3. **Graceful Fallback**: Revert to a rule-based/regex engine if NLP loading fails, ensuring zero-error startup.

## Alternatives Considered
- **Strict Dependency**: Force user to install model manually.
  - Cons: Terrible UX, high barrier to entry.
- **Pre-bundling Only**: Bundle model in EXE.
  - Cons: Increases EXE size by ~50-100MB; might still fail due to anti-virus or path issues.
- **Cloud NLP API**: Use an external API.
  - Cons: Requires internet, privacy concerns, introduces latency.

## Rationale
`spaCy` was chosen for its performance and accuracy in entity extraction compared to NLTK. The fallback logic ensures the application remains functional even in "lite" mode. Separating the model loading from the main app thread prevents startup crashes.

## Consequences
- **Benefits**: Robust user experience, cross-platform reliability, reduced technical debt regarding large assets.
- **Limitations**: Rule-based fallback is less "intelligent" (strict phrasing required), but logs and GUI guidance help the user adapt.
