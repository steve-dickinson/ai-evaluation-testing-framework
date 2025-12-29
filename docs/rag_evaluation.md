# 📚 RAG Metrics Evaluation

The **RAG Evaluation** module allows you to measure the quality of Retrieval-Augmented Generation systems using **LLM-as-a-Judge**.

Unlike standard "Pass/Fail" tests, RAG evaluation assesses *how* the chatbot answered, specifically looking for hallucinations and retrieval failures.

---

## Metrics

We currently compute three key scores (from 0.0 to 1.0):

### 1. Answer Relevance
*   **Question**: *Does the response actually answer the user's prompt?*
*   **Goal**: Ensure the chatbot isn't dodging the question or giving generic "I'm sorry" responses to valid queries.

### 2. Faithfulness (Groundedness)
*   **Question**: *Is the response purely derived from the provided context?*
*   **Goal**: Detect **Hallucinations**. If the bot invents facts that aren't in the source material, this score drops.

### 3. Context Recall
*   **Question**: *Did the response capture all the key facts from the Ground Truth?*
*   **Goal**: Measure completeness. If the context has the answer but the bot missed it, this score drops.

---

## How It Works: Reference-Based Evaluation

Since many external chatbots (like ChatGPT or specific websites) are "Black Boxes" where we can't see their internal retrieval logs, we use **Reference-Based Evaluation**.

You, as the tester, provide the **Ground Truth Context** in your test scenario. We then ask: *"Did the chatbot's answer match the facts in this Ground Truth?"*

### Example Test Scenario (`.yaml`)

```yaml
- id: "rag-refund-policy"
  name: "Refund Policy Check"
  prompt: "What is your refund policy?"
  # The "Gold Standard" truth the bot IS EXPECTED to know/find.
  context: "Returns are allowed within 30 days. No returns after that." 
  expected_behavior: "State the 30-day limit."
```

---

## Running RAG Tests

1.  **Create a Test Suite**: Ensure your `.yaml` file includes the `context` field for each scenario.
2.  **Open Dashboard**: Go to `http://localhost:8501`.
3.  **Run Mode**: Select `Standard Evaluation`.
4.  **Evaluator Type**: Select **`RAG Evaluation`**.
5.  **Run**: Click execute. The metrics will be displayed in the results table.
