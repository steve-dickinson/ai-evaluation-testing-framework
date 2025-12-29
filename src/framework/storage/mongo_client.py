from datetime import datetime
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from src.framework.models.data_models import TestResult

class MongoStorage:
    """
    Handles persistence of test runs and results to MongoDB.
    """

    def __init__(self, uri: str, db_name: str = "ai_eval_framework"):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            # Trigger connection check
            self.client.server_info()
            self.db = self.client[db_name]
            print(f"Connected to MongoDB at {uri}")
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            self.client = None

    def is_connected(self) -> bool:
        return self.client is not None

    def save_test_run(self, suite_name: str, results: List[TestResult], metadata: Dict[str, Any] = None) -> str:
        """
        Saves a test run. Returns the Run ID.
        """
        if not self.is_connected():
            return None

        # Calculate summary metrics
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        score = (passed / total) * 100 if total > 0 else 0

        run_doc = {
            "timestamp": datetime.utcnow(),
            "suite_name": suite_name,
            "total_tests": total,
            "passed_tests": passed,
            "pass_rate": score,
            "metadata": metadata or {},
            "results": [
                {
                    "scenario_id": r.scenario_id,
                    "prompt": r.prompt,
                    "response": r.response,
                    "passed": r.passed,
                    "score": r.score,
                    "metrics": r.metrics,
                    "error": r.error,
                    "execution_time_ms": r.execution_time_ms
                } for r in results
            ]
        }

        try:
            result = self.db.test_runs.insert_one(run_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")
            return None

    def get_recent_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetches the most recent test runs (summary only).
        """
        if not self.is_connected():
            return []

        cursor = self.db.test_runs.find({}, {
            "timestamp": 1, 
            "suite_name": 1, 
            "total_tests": 1, 
            "passed_tests": 1, 
            "pass_rate": 1
        }).sort("timestamp", -1).limit(limit)

        return list(cursor)

    def get_run_details(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches full details of a specific run properly converting ObjectId.
        """
        if not self.is_connected():
           return None
           
        from bson.objectid import ObjectId
        try:
            return self.db.test_runs.find_one({"_id": ObjectId(run_id)})
        except:
            return None
