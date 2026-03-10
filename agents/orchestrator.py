from pydantic import BaseModel
from typing import Literal
from user_profile.schema import SearchParams, State

class ExecuteIntent(BaseModel):
    """Call this to execute the user's intent"""
    intent: Literal[
        "full_search",
        "transcript_only", 
        "rerank_only",
        "profile_update",
        "out_of_scope"
    ]
    search_params: SearchParams | None = None
    video_id: str | None = None

def route_intent(state: State) -> str:
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]
    intent = tool_call["args"]["intent"]
    
    if intent == "full_search":
        return "search_agent"
    elif intent == "transcript_only":
        return "transcript_agent"
    elif intent == "rerank_only":
        return "scoring_agent"
    elif intent == "profile_update":
        return "profile_update_node"
    else:
        return END