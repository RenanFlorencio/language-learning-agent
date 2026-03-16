
from agents.transcripter import transcripter
from user_profile.schema import VideoInfo
from unittest.mock import MagicMock
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
        "videos": [VideoInfo(video_id='G_jN7icWjk4', title='POULET CHASSEUR | Une recette française, facile et incroyablement savoureuse', channel_id='UCSLyEx8ISkp567AjOAHYN5Q', channel_title='Chef Michel Dumas', CC=False, published_time='il y a 1 an', views=207381, detected_language=None, detected_level=None, for_students=None, score=None)],
        "user_profile": None
    }

    result = transcripter(state, config, store)
    print(result["videos"])