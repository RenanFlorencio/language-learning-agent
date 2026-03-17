from schemas.schema import State, VideoInfo
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from agents import video_scorer, video_searcher, video_transcripter
from langchain_core.messages import AIMessage
from typing import Literal
from langgraph.graph import END, START


def route_intent(state: State, config : RunnableConfig, store : BaseStore) -> Literal["__end__", "full_search_pipeline", "transcript_only_pipeline", "profile_update_agent"]:
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage):
        return "__end__"
    if not last_message.tool_calls:
        return "__end__"

    intent = last_message.tool_calls[0]["args"]["intent"] 
    print(f"Intent: {intent}")

    if intent == "full_search":
        return "full_search_pipeline"
    elif intent == "transcript_only":
        return "transcript_only_pipeline"
    elif intent == "profile_update":
        return "profile_update_agent"
    else:
        return "__end__"


def full_search_pipeline(state : State, config : RunnableConfig, store : BaseStore):
    state["videos"] = video_searcher.searcher(state, config, store)["videos"]
    state["videos"] = video_transcripter.transcripter(state, config, store)["videos"]
    state["videos"] = video_scorer.scorer(state, config, store)["videos"]

    video_summary = "\n".join([
        f"{i+1}. {v.title}\n"
        f"   Channel: {v.channel_title}\n"
        f"   Level: {v.detected_level} | Score: {v.score}/100\n"
        f"   Level Explanation: {v.level_explanation}\n"
        f"   Score Explanation: {v.score_explanation}\n"
        f"   For Students: {'Yes' if v.for_students else 'No'}\n"
        f"   URL: https://www.youtube.com/watch?v={v.video_id}"
        for i, v in enumerate(state["videos"])
    ])  

    last_message = state['messages'][-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError("Expected AIMessage with tool calls")
    tool_call_id = last_message.tool_calls[0]["id"]

    return {
        "videos": state["videos"],
        "messages" : [{"role" : "tool", "content" : f"Found {len(state['videos'])} scored videos\n{video_summary}", "tool_call_id": tool_call_id}]
    }


def transcript_only_pipeline(state: State, config : RunnableConfig, store : BaseStore):
    if not state["video_id"]:
        raise ValueError("No video_id provided for transcript_only_pipeline")
    
    video_id = state["video_id"]
    # The transcript agent nesses a video to operate, just create a basic one
    state["videos"] = [VideoInfo(
        video_id=video_id,
        title="Unknown",
        channel_id="Unknown",
        channel_title="Unknown",
        CC=False,
        published_time="Unknown",
        views=0
    )]
    state["videos"] = video_transcripter.transcripter(state, config, store)["videos"]
    if state["videos"] == None:
        return {"videos": {}}

    last_message = state['messages'][-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError("Expected AIMessage with tool calls")
    tool_call_id = last_message.tool_calls[0]["id"]

    return {
        "videos": state["videos"],
        "messages" : [{"role" : "tool", "content" : f"Detected level of {len(state['videos'])} videos.", "tool_call_id": tool_call_id}]
    }

