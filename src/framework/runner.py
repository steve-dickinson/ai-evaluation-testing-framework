import time
from typing import List
from src.framework.core.interfaces import BaseChatbot, BaseEvaluator
from src.framework.models.data_models import TestScenario, TestResult

class TestRunner:
    """Orchestrates the execution of test scenarios."""

    def __init__(self, chatbot: BaseChatbot, evaluator: BaseEvaluator):
        self.chatbot = chatbot
        self.evaluator = evaluator

    def run_scenario(self, scenario: TestScenario) -> TestResult:
        """Runs a single test scenario."""
        start_time = time.time()
        
        try:
            # 1. Send prompt to chatbot
            response_text = self.chatbot.send_message(scenario.prompt, context=scenario.metadata)
            
            # 2. Evaluate response
            eval_result = self.evaluator.evaluate(
                prompt=scenario.prompt,
                response=response_text,
                context=scenario.metadata
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            return TestResult(
                scenario_id=scenario.id,
                prompt=scenario.prompt,
                response=response_text,
                passed=eval_result.get("passed", False),
                score=eval_result.get("score", 0.0),
                metrics=eval_result,
                execution_time_ms=execution_time
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return TestResult(
                scenario_id=scenario.id,
                prompt=scenario.prompt,
                response="",
                passed=False,
                score=0.0,
                error=str(e),
                execution_time_ms=execution_time
            )

    def run_suite(self, scenarios: List[TestScenario]) -> List[TestResult]:
        """Runs a list of scenarios."""
        results = []
        for scenario in scenarios:
            results.append(self.run_scenario(scenario))
        return results
