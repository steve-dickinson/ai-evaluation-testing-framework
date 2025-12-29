# Usage Guide

## Running Tests

### 1. Interactive Dashboard (Recommended)
The main interface is the Streamlit Dashboard, which provides:
- **Test Execution**: Run suites against OpenAI APIs or specific URLs (UI Testing).
- **History**: View past test runs stored in MongoDB.
- **Recommendations**: Analyze failures and get automatic system prompt revisions.

```bash
uv run streamlit run src/dashboard.py
```

#### New Features:
- **📜 History**: Access the "History" tab to view and **Load** previous test runs from MongoDB. This allows you to review past results without re-running tests.
- **🛡️ Recommendations**: If tests fail, use the "Analyze Failures" button. The AI will analyze the failure patterns and suggest a **Revised System Prompt** to fix the security or accuracy issues.

### 2. Command Line Interface (CLI)
For CI/CD pipelines, use the CLI:

```bash
uv run python -m src.main --config <path_to_config.yaml>
```

#### Options
- `--config`: Path to the YAML configuration file (default: `tests/simple_suite.yaml`).
- `--mock`: Run with a mock OpenAI client.
- `--url`: URLs for Playwright testing.
- `--evaluator`: Choose `keyword` or `llm_judge`.

## Test Configuration

Test suites are defined in YAML.

```yaml
scenarios:
  - id: "unique-id"
    name: "Scenario Name"
    prompt: "The prompt to send to the chatbot"
    metadata:
      system_prompt: "Optional system prompt"
```

## Adding New Chatbots

To add a new chatbot provider, subclass `BaseChatbot` in `src/framework/core/interfaces.py`:

```python
class MyChatbot(BaseChatbot):
    def send_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        # Implement your API call here
        return "response"
```

## Adding New Evaluators

To add a new evaluation logic, subclass `BaseEvaluator`:

```python
class MyEvaluator(BaseEvaluator):
    def evaluate(self, prompt: str, response: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Implement logic
        return {"passed": True, "score": 1.0}
```
