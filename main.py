import os
from graph import build_graph
from langchain.messages import HumanMessage
import uuid

if __name__ == "__main__":

    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = "language-learning-agent"

    graph, store = build_graph()

    memories = store.search(("profile", "test_user"))
    print("Profile before:", memories[0].value if memories else "empty")
    
    result = graph.invoke(
    {"messages": [HumanMessage(content="I like cinema")]},
    config={
        "configurable": {
            "thread_id": f"{uuid.uuid4()}",
            "user_id": "test_user"
            }
        }
    )

    memories = store.search(("profile", "test_user"))
    print("Current profile:", memories[0].value if memories else "empty")