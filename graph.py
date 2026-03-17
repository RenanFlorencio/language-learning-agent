# graph.py
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.store.sqlite import SqliteStore
import sqlite3

from agents.orchestrator import orchestrator
from agents.pipelines import route_intent, full_search_pipeline, transcript_only_pipeline
from agents.profile_updater import profile_updater
from schemas.schema import State
import configuration

def build_graph():
    builder = StateGraph(State, config_schema=configuration.Configuration) # type: ignore
    builder.add_node("orchestrator", orchestrator)
    builder.add_node("full_search_pipeline", full_search_pipeline)
    builder.add_node("transcript_only_pipeline", transcript_only_pipeline)
    builder.add_node("profile_update_agent", profile_updater)

    builder.add_edge(START, "orchestrator")
    builder.add_conditional_edges("orchestrator", route_intent)
    builder.add_edge("full_search_pipeline", "orchestrator")
    builder.add_edge("transcript_only_pipeline", "orchestrator")
    builder.add_edge("profile_update_agent", "orchestrator")

    # Store long-term
    conn = sqlite3.connect(
    "profile.db",
    check_same_thread=False,  # allow access from multiple threads
    isolation_level=None       # autocommit mode — lets SqliteStore manage transactions
    )
    store = SqliteStore(conn)
    store.setup()
    # Store short-term
    in_thread_memory = MemorySaver()

    graph = builder.compile(checkpointer=in_thread_memory, store=store)

    # View
    return graph, store