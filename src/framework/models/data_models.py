from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class TestScenario(BaseModel):
    """Defines a single test scenario."""
    id: str
    name: str
    description: Optional[str] = None
    prompt: str
    expected_behavior: Optional[str] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class TestResult(BaseModel):
    """Records the result of a test execution."""
    scenario_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    prompt: str
    response: str
    passed: bool
    score: float
    metrics: Dict[str, Any] = {}
    error: Optional[str] = None
    execution_time_ms: float = 0.0
