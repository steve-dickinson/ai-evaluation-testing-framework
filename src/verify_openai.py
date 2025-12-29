import os
import yaml
from unittest.mock import MagicMock
from src.framework.core.interfaces import BaseEvaluator
from src.framework.chatbot.openai_client import OpenAIChatbot
from src.framework.runner import TestRunner
from src.framework.models.data_models import TestScenario

# Mock Evaluator for basic testing
class SimpleEvaluator(BaseEvaluator):
    def evaluate(self, prompt, response, context=None):
        return {"passed": True, "score": 1.0, "reason": "Always passes"}

def load_scenarios(path):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return [TestScenario(**item) for item in data["scenarios"]]

def main():
    print("Starting verification...")
    
    # Check for API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("WARNING: No OPENAI_API_KEY found. Using Mock client.")
        client = OpenAIChatbot(api_key="mock-key")
        # Mock the internal OpenAI client to avoid actual calls
        client.client.chat.completions.create = MagicMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content="This is a mocked response."))]
        ))
    else:
        print("Using actual OpenAI client.")
        client = OpenAIChatbot()

    evaluator = SimpleEvaluator()
    runner = TestRunner(client, evaluator)
    
    scenarios = load_scenarios("tests/simple_suite.yaml")
    results = runner.run_suite(scenarios)
    
    print(f"\nRan {len(results)} tests.")
    for res in results:
        print(f"[{'PASS' if res.passed else 'FAIL'}] {res.scenario_id}: {res.response[:50]}...")

if __name__ == "__main__":
    main()
