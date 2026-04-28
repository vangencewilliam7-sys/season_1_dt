"""
providers/mock_llm.py

Mock LLM Provider for offline testing and demonstrations.
Returns pre-canned responses based on the prompt type.

Use when:
- No internet access / API key is available
- Demonstrating the pipeline flow without spending tokens
- Running continuous integration tests
"""

import json
import logging
from typing import List

from core.providers.base_llm import BaseLLMProvider

logger = logging.getLogger(__name__)


class MockLLMProvider(BaseLLMProvider):
    """
    Mock LLM provider for testing the extraction framework.
    """

    def __init__(self, model_id: str = "mock-model"):
        self.model_id = model_id
        logger.info(f"[MockLLM] Initialised with model: {model_id}")

    def chat(
        self,
        messages: List[dict],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """
        Return a mock JSON response depending on the last message/system prompt.
        """
        system_prompt = messages[0]["content"] if messages[0]["role"] == "system" else ""
        
        # 1. Ingestion Node Mock
        if "deep semantic scan" in system_prompt.lower():
            return json.dumps({
                "hypotheses": [
                    "Prioritizes system stability and simplicity over complex microservices (evidenced by 'Flash Sale' case).",
                    "Favor asynchonous event-driven patterns for high-scale availability.",
                    "Views technology migration as primary leverage for organizational modernization.",
                    "Strictly blocks architectures that do not define a clear threat model."
                ],
                "observed_knowledge_gaps": ["Mobile UX design", "Legacy Mainframe COBOL", "Frontend Frameworks"]
            })

        # 2. Journalist Questions Mock
        if "ai journalist" in system_prompt.lower():
            return json.dumps({
                "validation_questions": [
                    {
                        "question": "The team wants to rewrite the legacy billing module in React Native. What is your stance?",
                        "tests_hypothesis": "Modernization leverage",
                        "expected_reveal": "Decision logic around mobile vs serverless"
                    },
                    {
                        "question": "A new sale is coming. The DB is the bottleneck. Why not use NoSQL?",
                        "tests_hypothesis": "Stability over trend",
                        "expected_reveal": "Simplicity preference"
                    }
                ],
                "boundary_questions": [
                    {
                        "question": "How would you optimize the CSS rendering performance of a dashboard?",
                        "boundary_area": "Frontend Frameworks"
                    }
                ]
            })

        # 3. Answer Processor Mock (Step 6a)
        if "analyzing an expert's manual answers" in system_prompt.lower() or "extract structured behavioral patterns" in system_prompt.lower():
            return json.dumps({
                "confirmed_heuristics": [
                    {
                        "trigger": "When a performance bottleneck exists in a legacy DB during a time-sensitive period",
                        "decision": "Use redis caching/buffering instead of a DB migration",
                        "reasoning": "Stability is more important than the 'perfect' DB when deadlines are short"
                    },
                    {
                        "trigger": "When presented with a legacy migration request",
                        "decision": "Force decomposition of the monolith into serverless/modern components",
                        "reasoning": "Migration is the ONLY time you have political leverage to fix architectural debt"
                    }
                ],
                "confirmed_drop_zones": ["Frontend performance tuning", "Mobile application design"],
                "communication_style": {
                    "tone": ["direct", "pragmatic", "skeptical of hype"],
                    "verbosity": "concise",
                    "preferred_framing": "Risk-first evaluation"
                }
            })

        return "Mock response for generic prompt."

    def get_model_id(self) -> str:
        return self.model_id
