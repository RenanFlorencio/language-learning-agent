# graph.py
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.store.sqlite import SqliteStore
import sqlite3

from agents.news_searcher import news_searcher
from agents.orchestrator import orchestrator
from agents.pipelines import route_intent, youtube_search_pipeline, transcript_only_pipeline
from agents.profile_updater import profile_updater
from schemas.schema import State
import configuration


_conn = sqlite3.connect("profile.db", check_same_thread=False, isolation_level=None)
_store = SqliteStore(_conn)
_store.setup()  # runs once at import time, before ASGI server starts

def build_graph():
    builder = StateGraph(State, config_schema=configuration.Configuration) # type: ignore
    builder.add_node("orchestrator", orchestrator)
    builder.add_node("youtube_search", youtube_search_pipeline)
    builder.add_node("transcript_only_pipeline", transcript_only_pipeline)
    builder.add_node("profile_update_agent", profile_updater)
    builder.add_node("news_search_agent", news_searcher)

    builder.add_edge(START, "orchestrator")
    builder.add_conditional_edges("orchestrator", route_intent)
    builder.add_edge("youtube_search", "orchestrator")
    builder.add_edge("transcript_only_pipeline", "orchestrator")
    builder.add_edge("profile_update_agent", "orchestrator")
    builder.add_edge("news_search_agent", "orchestrator")
    
    # Store short-term
    in_thread_memory = MemorySaver()

    graph = builder.compile(checkpointer=in_thread_memory, store=_store)

    return graph