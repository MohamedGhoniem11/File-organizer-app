# FUTURE PLAN: NLP Chatbot for File Search

## Objective
To allow users to search for and interact with their files using natural language.

## Proposed Architecture
The NLP feature will be integrated as a new service in `src/services/nlp_service.py` and a new tab in the GUI.

### Phase 1: Semantic Metadata Extraction
- Implement a background service that indexes files.
- Extract basic tags using lightweight NLP (e.g., `sentence-transformers`).
- Store embeddings in a local vector DB (e.g., `ChromaDB` or a simple JSON index).

### Phase 2: Natural Language Interface
- Integrate a local LLM or an API-based assistant.
- Users can type queries like:
  - "Organize my desktop into subfolders based on project names."
  - "Find the invoice from Amazon I received yesterday."
- The chatbot will interact with the `Core Engine` to perform actions.

### Phase 3: Actionable Conversations
- "Clean up my Downloads folder."
- "Zip all my project files and move them to Archives."

## Technology Stack
- **NLP Library**: `sentence-transformers` for embeddings.
- **Interface**: `LangChain` for orchestration.
- **GUI**: New "Chat" frame in `src/gui/chat.py`.
