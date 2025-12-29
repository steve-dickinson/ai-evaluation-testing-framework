import os
import yaml
import argparse
from typing import List, Optional
from dotenv import load_dotenv
from unittest.mock import MagicMock

# Load environment variables
load_dotenv()

from src.framework.chatbot.openai_client import OpenAIChatbot
from src.framework.chatbot.playwright_client import PlaywrightChatbot
from src.framework.evaluators.content_safety import ContentSafetyEvaluator
from src.framework.evaluators.llm_evaluator import LLMEvaluator
from src.framework.runner import TestRunner
from src.framework.models.data_models import TestScenario
from src.framework.core.interfaces import BaseChatbot, BaseEvaluator

def load_scenarios(path: str) -> List[TestScenario]:
    """Loads test scenarios from a YAML file."""
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return [TestScenario(**item) for item in data.get("scenarios", [])]

def get_chatbot(target_url: Optional[str] = None, mock: bool = False) -> BaseChatbot:
    """Factory function to initialize the appropriate chatbot client."""
    if target_url:
        print(f"Using Playwright Chatbot targeting: {target_url}")
        return PlaywrightChatbot(target_url=target_url, headless=True)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if mock or not api_key:
        print("Using MOCK OpenAI client.")
        bot = OpenAIChatbot(api_key="mock-key")
        # Configure mock response
        bot.client.chat.completions.create = MagicMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content="[MOCK] Safe response."))]
        ))
        return bot
    
    print("Using REAL OpenAI client.")
    return OpenAIChatbot()

def get_evaluator(evaluator_type: str, chatbot: BaseChatbot, mock: bool = False) -> BaseEvaluator:
    """Factory function to initialize the evaluator."""
    if evaluator_type == "llm":
        print("Using LLM Evaluator (Judge).")
        if mock:
             # Use a mock judge 
            judge_client = OpenAIChatbot(api_key="mock-key")
            judge_client.client.chat.completions.create = MagicMock(return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content='{"passed": true, "score": 0.9, "reason": "Mock judge approves."}'))]
            ))
            return LLMEvaluator(judge_client)
        
        # Reuse the chatbot client if it's an OpenAIChatbot, otherwise create fresh
        if isinstance(chatbot, OpenAIChatbot):
            return LLMEvaluator(chatbot)
        return LLMEvaluator(OpenAIChatbot()) # Fresh client for judge
        
    print("Using Keyword Content Safety Evaluator.")
    return ContentSafetyEvaluator()

def main():
    parser = argparse.ArgumentParser(description="AI Chatbot Evaluation Framework")
    parser.add_argument("--config", type=str, default="tests/simple_suite.yaml", help="Path to test suite config")
    parser.add_argument("--mock", action="store_true", help="Use mock OpenAI client")
    parser.add_argument("--evaluator", type=str, default="keyword", choices=["keyword", "llm"], help="Type of evaluator to use")
    parser.add_argument("--target-url", type=str, default=None, help="Target URL for Playwright testing")
    args = parser.parse_args()

    print(f"Loading configuration from {args.config}...")
    try:
        scenarios = load_scenarios(args.config)
    except FileNotFoundError:
        print(f"Error: Config file '{args.config}' not found.")
        return

    # Initialize Components
    chatbot = get_chatbot(args.target_url, args.mock)
    evaluator = get_evaluator(args.evaluator, chatbot, args.mock)
    
    # Run Tests
    runner = TestRunner(chatbot, evaluator)
    results = runner.run_suite(scenarios)
    
    # Report
    print(f"\nExecution Complete. Ran {len(results)} tests.\n")
    pass_count = sum(1 for res in results if res.passed)
    
    for res in results:
        status = "PASS" if res.passed else "FAIL"
        print(f"[{status}] {res.scenario_id}: Score={res.score} | Reason={res.metrics.get('reason')}")
        if res.error:
            print(f"       ERROR: {res.error}")
        print("-" * 50)
        
    print(f"\nSummary: {pass_count}/{len(results)} Passed.")

if __name__ == "__main__":
    main()
