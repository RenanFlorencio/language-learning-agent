from unittest.mock import MagicMock
from agents import orchestrator
from langchain.messages import HumanMessage

if __name__ == "__main__":

    config = {"configurable": {"user_id": "test_user"}}
        
    store = MagicMock()
    store.search.return_value = []  # empty profile

    # Mock state with a user message 
    state = {
        "messages": [HumanMessage(content="Find me German cooking videos at B1")],
        "search_params": None,
        "videos": None,
        "user_profile": None
    }

    result = orchestrator.orchestrator(state, config, store)
    print(result["search_params"])