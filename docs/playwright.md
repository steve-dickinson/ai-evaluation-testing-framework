# Playwright Integration

The framework handles **End-to-End (E2E)** testing using [Playwright](https://playwright.dev/). This allows it to interact with web-based chatbots just like a human user would—by typing into input fields and reading responses from the DOM.

## How it Works
1.  **Browser Launch**: The `PlaywrightChatbot` adapter launches a Chromium browser (headless by default).
2.  **Navigation**: It navigates to the `target_url` provided.
3.  **Interaction**:
    - Finds the chat input (heuristic: `textarea`, `aria-label="Ask me anything..."`).
    - Types the prompt and presses Enter.
4.  **Scraping**:
    - Waits for the response implementation.
    - Extracts the text of the latest message.

## Configuration

### CLI
```bash
uv run python -m src.main --target-url http://localhost:8503 --evaluator llm
```

### Dashboard
1.  Select **"Playwright (UI Testing)"** in the Sidebar.
2.  Enter the **Target App URL** (e.g., `http://localhost:8503`).
3.  Ensure the target app is running!

## Requirements
- `playwright` python package.
- Browsers installed (`playwright install`).
- **System Dependencies**: You may need to run:
  ```bash
  uv run playwright install-deps
  ```
  (Requires sudo/admin privileges).
