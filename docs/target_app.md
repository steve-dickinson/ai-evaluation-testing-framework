# Target Chatbot & RAG

The framework includes a reference implementation of an AI Chatbot (`src/target_app.py`) to serve as a "System Under Test".

## Features
- **Streamlit Interface**: A standard chat UI.
- **RAG (Retrieval-Augmented Generation)**: Answers are grounded in documents found in the `data/` directory.
- **Multi-File Support**: Automatically loads all `.txt` and `.md` files in `data/`.
- **System Prompt**: Enforces strict adherence to the provided context.

## Running the App
```bash
uv run streamlit run src/target_app.py --server.port 8503
```
*Note: We use port 8503 to avoid conflict with the dashboard running on 8501.*

## Knowledge Base
To update the chatbot's knowledge, simply add or edit files in the `data/` directory. The bot scans this folder on startup.

Example structure:
```text
data/
├── knowledge_base.txt
├── secret_protocols.md
└── project_info.txt
```

## Testing Groundedness
You can write test scenarios to verify the bot uses this data:

```yaml
- id: "rag-check"
  prompt: "What is the secret code?"
  expected_behavior: "Should answer 'Blue-7'"
```
