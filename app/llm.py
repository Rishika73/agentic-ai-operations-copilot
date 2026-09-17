import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()


def get_openai_client():
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured.")

    return OpenAI(
        api_key=api_key,
        timeout=30.0
    )


def generate_operational_answer(
    user_query: str,
    route: str,
    tool_results: List[Dict[str, Any]] | None = None,
    retrieved_context: List[Dict[str, Any]] | None = None,
) -> str:

    payload = {
        "route": route,
        "tool_results": tool_results or [],
        "retrieved_context": retrieved_context or [],
    }

    prompt = f"""
You are an enterprise AI operations copilot.

Answer the user's question using ONLY the supplied operational data.

Rules:
- Do not invent facts.
- Clearly identify important incidents, account risks, or policies.
- Prioritize critical and high-risk information.
- If information is unavailable, say so.
- Keep the response concise and operational.
- Do not mention internal routing implementation details.
- Never claim that you performed or can perform an action unless a real tool exists for that action.
- Do not offer to escalate, notify, modify, or execute operational changes unless an execution tool is available.

User question:
{user_query}

Operational data:
{json.dumps(payload, indent=2)}
"""

    client = get_openai_client()

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return response.output_text
