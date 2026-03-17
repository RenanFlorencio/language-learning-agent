from unittest.mock import MagicMock
from agents import news_searcher
from langchain.messages import AIMessage, HumanMessage


if __name__ == "__main__":
    config = {"configurable": {"user_id": "test_user"}}
        
    store = MagicMock()
    store.search.return_value = []  # empty profile

    # Mock state with a user message 
    state = {
        "messages": [
            HumanMessage(content="Find me relevant news in French"),
            AIMessage( # Here we simulate the orchestrator's tool call message to trigger the news search agent
                content="",
                tool_calls=[{
                    "name": "ExecuteIntent",
                    "args": {"intent": "news_search", "news_search_params": {"language": "fr"}},
                    "id": "call_test_123",
                    "type": "tool_call"
                }]
            )
        ],
        "news_search_params": {"language": "fr"},
        "videos": None,
        "news_articles": None,
    }
    result = news_searcher.news_searcher(state, config, store)
    print("\n====== MESSAGES =====\n", result["messages"])
    print("\n====== ARTICLES =====\n", result["news_articles"])
