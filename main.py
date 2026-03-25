import os
from graph import build_graph
from langchain.messages import HumanMessage
import uuid

if __name__ == "__main__":

    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = "language-learning-agent"

    graph = build_graph()

    memories = graph.store.search(("profile", "test_user"))
    print("Profile before:", memories[0].value if memories else "empty")
    
    result = graph.invoke(
    {"messages": [HumanMessage(content="Analyze this spanish video: https://www.youtube.com/watch?v=QMQyUoKx868")]},
    config={
        "configurable": {
            "thread_id": f"{uuid.uuid4()}",
            "user_id": "test_user"
            }
        }
    )

    memories = graph.store.search(("profile", "test_user"))
    print("Current profile:", memories[0].value if memories else "empty")
    print("Final response:\n", result["messages"][-1].content)
    print("News articles returned by tool:\n", result.get("news", []))