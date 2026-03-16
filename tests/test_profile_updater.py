import uuid
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.store.memory import InMemoryStore
from user_profile.schema import UserProfile, SearchParams
from agents.profile_updater import profile_updater

if __name__ == "__main__":
# Real in-memory store
    store = InMemoryStore()

    # Put the mock profile into the store
    user_id = "test_user"
    namespace = ("profile", user_id)
    mock_profile = UserProfile(
        interests=["history", "gastronomy"],
        dislikes=["reality TV", "sports"],
        languages=["English", "French"],
        language_levels={"English": "C2", "French": "A2"},
        saved_channels_id=["UCcinema123", "UChistoire456"],
        channel_ratings={
            "UCcinema123": 5.0,
            "UCreality789": 1.0
        },
        video_ratings={
            "vid_easy_french": 5.0,
            "vid_hard_debate": 1.0
        }
    )

    # Store the profile with a fixed key
    store.put(namespace, str(uuid.uuid4()), mock_profile.model_dump())

    config = {"configurable": {"user_id": user_id}}

    state = {
        "messages": [
            HumanMessage(content="I'm starting to learn Spanish and I like cinema"),
            AIMessage(content="", tool_calls=[{
                "name": "ExecuteIntent",
                "args": {"intent": "profile_update"},
                "id": "call_123",
                "type": "tool_call"
            }])
        ],
        "search_params": SearchParams(
            topic="cinema",
            language="fr",
            target_level="A2",
            max_results=10
        ),
        "videos": None,
    }

    results = profile_updater(state, config, store)
    print("Profile update results:", results['messages'][-1]["content"])
    print("Updated profile:", store.search(namespace)[0].value)

    assert "Spanish" in store.search(namespace)[0].value["languages"]
    assert ("Spanish", "A1") in store.search(namespace)[0].value["language_levels"].items()
    assert "cinema" in store.search(namespace)[0].value["interests"]