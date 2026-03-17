from unittest.mock import MagicMock
from agents import video_searcher
from langchain.messages import HumanMessage


if __name__ == "__main__":
    config = {"configurable": {"user_id": "test_user"}}
        
    store = MagicMock()
    store.search.return_value = []  # empty profile

    # Mock state with a user message 
    state = {
        "messages": [HumanMessage(content="Find me French cooking videos at B1")],
        "search_params": {
            'topic': 'cooking',
            'language': 'fr',
            'target_level': 'B1',
            'max_results': 10
            },
        "videos": None,
        "user_profile": None
    }

    result = video_searcher.searcher(state, config, store)
    print(result["videos"])