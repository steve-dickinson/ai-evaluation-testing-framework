# System Architecture

## Overview

The AI Chatbot Evaluation Framework is designed as a modular system to test and evaluate LLM-based chatbots.

## Core Components

### 1. Test Runner
The `TestRunner` class orchestrates the execution. It takes a `Chatbot` and an `Evaluator`, runs a list of `TestScenario`s, and produces `TestResult`s.

### 2. Interfaces
- **BaseChatbot**: Abstract interface for chatbot backends.
- **BaseEvaluator**: Abstract interface for evaluation logic.

### 3. Data Models
- **TestScenario**: Input data defining the test (prompt, metadata).
- **TestResult**: Output data containing the prompt, response, and evaluation metrics.

### 4. Evaluators
- **ContentSafetyEvaluator**: Keyword-based blocking.
- **LLMEvaluator**: Uses an LLM (as a Judge) to evaluate nuance, tone, and refusal behavior.

### 5. Storage (MongoDB)
- **MongoStorage**: Handles persistence of test runs and results for historical analysis.

### 6. Intelligent Analysis
- **RecommendationEngine**: Analyzes failed tests to suggest System Prompt improvements using an LLM.

## Data Flow

1.  **Load Config**: YAML configuration is loaded into `TestScenario` objects.
2.  **Initialize**: `Chatbot` and `Evaluator` are initialized.
3.  **Execute**:
    - `TestRunner` sends prompt to `Chatbot`.
    - `Chatbot` returns response.
    - `TestRunner` sends response to `Evaluator`.
    - `Evaluator` returns metrics.
4.  **Report**: Results are aggregated and printed/logged.
