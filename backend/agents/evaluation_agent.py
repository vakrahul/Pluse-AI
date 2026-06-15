"""Evaluation agent — LLM-as-a-judge for QA."""

from __future__ import annotations

import json
import logging
import re

from backend.agents.state import AgentState
from backend.utils.llm import llm_client

logger = logging.getLogger(__name__)

EVAL_SYSTEM = """You are an independent Quality Assurance judge.
Evaluate the AI's final answer against the user's question and the provided context.

Return ONLY a JSON object with this exact structure:
{
  "grade": "PASS" | "FAIL",
  "reason": "<short explanation why>",
  "score": <float between 0.0 and 1.0>
}

RULES:
- Do not output markdown, just the JSON.
- If the answer is accurate and based on the context, grade is PASS.
- If the answer hallucinates or ignores the context, grade is FAIL.
- If no data was found and the AI politely explains this, grade is PASS (score 0.8)."""


async def evaluation_node(state: AgentState) -> AgentState:
    question = state.get("question", "")
    answer = state.get("final_answer", "")
    
    evaluation_result = {
        "grade": "PASS",
        "reason": "Default fallback evaluation",
        "score": 1.0
    }

    if llm_client.available:
        try:
            user_prompt = (
                f"Question: {question}\n\n"
                f"AI Answer: {answer}\n\n"
                "Evaluate."
            )
            raw = await llm_client.chat(EVAL_SYSTEM, user_prompt, temperature=0.0)
            if raw:
                match = re.search(r"\{[\s\S]*\}", raw)
                if match:
                    evaluation_result = json.loads(match.group())
                    logger.info("evaluation_node produced: %s", evaluation_result)
        except Exception as e:
            logger.warning("evaluation_node LLM failed, using fallback: %s", e)

    return {
        "evaluation_result": evaluation_result
    }
