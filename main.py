import os
from graph import build_graph
from langchain.messages import HumanMessage
import uuid

if __name__ == "__main__":

    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = "language-learning-agent"

    graph, store = build_graph()
    
    result = graph.invoke(
    {"messages": [HumanMessage(content="Find me 5 French cooking videos at B1")]},
    config={
        "configurable": {
            "thread_id": f"{uuid.uuid4()}",
            "user_id": "test_user"
            }
        }
    )
