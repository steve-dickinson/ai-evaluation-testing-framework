from src.framework.core.interfaces import BaseChatbot, BaseEvaluator
from src.framework.models.data_models import TestScenario

def test_imports():
    """Simple test to verify modules can be imported."""
    assert BaseChatbot is not None
    assert BaseEvaluator is not None
    assert TestScenario is not None

def test_scenario_creation():
    """Verify we can instantiate a scenario."""
    ts = TestScenario(id="test", name="Test", prompt="Hello")
    assert ts.id == "test"
