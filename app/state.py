from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict, total=False):
    user_query: str

    route: str

    retrieved_context: List[Dict[str, Any]]

    tool_results: List[Dict[str, Any]]

    final_answer: str

    proposed_action: Dict[str, Any]

    requires_approval: bool

    approval_status: str

    action_result: Dict[str, Any]
