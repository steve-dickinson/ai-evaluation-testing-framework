from typing import Any, Dict, Optional
from src.framework.core.interfaces import BaseEvaluator
from src.framework.chatbot.openai_client import OpenAIChatbot

class RAGEvaluator(BaseEvaluator):
    """
    Evaluates RAG quality using an LLM to measure Faithfulness and Answer Relevance.
    """
    def __init__(self, judge_client: OpenAIChatbot):
        self.judge_client = judge_client

    def evaluate(self, prompt: str, response: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Computes RAG metrics.
        - Answer Relevance: Does it answer the user prompt?
        - Faithfulness: Is the response supported by the Context (Ground Truth or Retrieved)?
        - Context Recall: (If Ground Truth available) Did the response capture the key facts?
        """
        context_dict = context or {}
        gt_context = context_dict.get("rag_context")
        
        metrics = {}
        total_score = 0.0
        count = 0

        relevance = self._evaluate_relevance(prompt, response)
        metrics["answer_relevance"] = relevance
        total_score += relevance
        count += 1

        if gt_context:
            faithfulness = self._evaluate_faithfulness(response, gt_context)
            metrics["faithfulness"] = faithfulness
            total_score += faithfulness
            count += 1
            
            recall = self._evaluate_context_recall(response, gt_context)
            metrics["context_recall"] = recall
            total_score += recall
            count += 1
        
        final_score = total_score / count if count > 0 else 0.0
        
        return {
            "passed": final_score >= 0.7,
            "score": final_score,
            **metrics
        }

    def _evaluate_relevance(self, prompt: str, response: str) -> float:
        system_prompt = (
            "You are an expert evaluator. "
            "Rate the relevance of the Response to the User Query on a scale of 0.0 to 1.0. "
            "1.0 means the response directly and fully covers the query. "
            "0.0 means the response is completely unrelated. "
            "Output ONLY the numeric score."
        )
        return self._get_score(system_prompt, f"User Query: {prompt}\nResponse: {response}")

    def _evaluate_faithfulness(self, response: str, context: str) -> float:
        system_prompt = (
            "You are an expert fact-checker. "
            "Rate the faithfulness of the Response to the provided Context on a scale of 0.0 to 1.0. "
            "1.0 means every claim in the response is directly supported by the context. "
            "0.0 means the response contains pure hallucinations or contradictions. "
            "Output ONLY the numeric score."
        )
        return self._get_score(system_prompt, f"Context: {context}\nResponse: {response}")

    def _evaluate_context_recall(self, response: str, context: str) -> float:
        system_prompt = (
            "You are an expert evaluator. "
            "Rate the Context Recall of the response on a scale of 0.0 to 1.0. "
            "Does the response contain all the key facts from the Ground Truth Context? "
            "1.0 = All key facts included. "
            "0.0 = No key facts included. "
            "Output ONLY the numeric score."
        )
        return self._get_score(system_prompt, f"Ground Truth Context: {context}\nResponse: {response}")

    def _get_score(self, system_prompt: str, user_message: str) -> float:
        try:
            score_str = self.judge_client.send_message(
                 user_message, 
                 context={"system_prompt": system_prompt}
            )
            return float(score_str.strip())
        except Exception as e:
            print(f"RAG Evaluator Error: {e}")
            return 0.0
