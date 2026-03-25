from schemas.schema import State, VideoInfo
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from agents import video_scorer, video_searcher, video_transcripter
from langchain_core.messages import AIMessage
from typing import Literal
from langgraph.graph import END, START


def route_intent(state: State, config : RunnableConfig, store : BaseStore) -> Literal["__end__", "youtube_search", "transcript_only_pipeline", "profile_update_agent", "news_search_agent"]:
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage):
        return "__end__"
    if not last_message.tool_calls:
        return "__end__"

    intent = last_message.tool_calls[0]["args"]["intent"] 
    print(f"Intent: {intent}")

    if intent == "youtube_search":
        return "youtube_search"
    elif intent == "transcript_only":
        return "transcript_only_pipeline"
    elif intent == "profile_update":
        return "profile_update_agent"
    elif intent == "news_search":
        return "news_search_agent"
    else:
        return "__end__"


def youtube_search_pipeline(state : State, config : RunnableConfig, store : BaseStore):
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
    last_message = state['messages'][-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError("Expected AIMessage with tool calls")
    tool_call_id = last_message.tool_calls[0]["id"]
    
    if not state["transcript_params"]:
        return {"videos": None,
                "messages" : [{"role" : "tool", "content" : 
                    f"No transcript parameters provided for transcript_only_pipeline. Please provide the video ID and target language and call the tool again.", "tool_call_id": tool_call_id}] 
                }
    
    video_id = state["transcript_params"]["video_id"]
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

    v = state["videos"][0]
    summary = f"""Transcript analysis for video {video_id}:\n
    - Detected language: {v.detected_language}\n"
    - Detected level: {v.detected_level}\n"
    - Explanation: {v.level_explanation}\n"
    """

    return {
        "videos": state["videos"],
        "messages" : [{"role" : "tool", "content" : summary, "tool_call_id": tool_call_id}]
    }

