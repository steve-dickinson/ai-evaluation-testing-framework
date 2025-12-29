# AI Evaluation & Testing Framework
Documentation for the automated testing and evaluation framework for AI Chatbots.

!!! caution "Disclaimer"
    This project is a **personal experiment** and proof-of-concept. It is **not intended for production use**. Use at your own risk.

## Overview
This framework provides a suite of tools to evaluate AI chatbots for safety, accuracy, and performance using both API and UI interactions.

## Contents

### 🚀 Getting Started
-   [**Usage Guide**](usage.md): How to configure and run tests.
-   [**Docker & Deployment**](docker.md): Running the full stack with Docker Compose.

### 🧩 Components
-   [**Target Chatbot (RAG)**](target_app.md): The reference AI application with Knowledge Base support.
-   [**Evaluators**](evaluators.md): LLM-as-a-Judge and Content Safety capabilities.
-   [**Playwright UI Testing**](playwright.md): Testing web-based chatbots via UI automation.

### 🏗️ Architecture
-   [**System Design**](architecture.md): High-level overview of the framework components.

## Key Features
-   **Streamlit Dashboard**: Interactive control center.
-   **MongoDB History**: Persistent storage of test runs.
-   **Recommendation Engine**: AI-driven analysis of failure modes.
- [**Architecture**](architecture.md): Technical overview.
