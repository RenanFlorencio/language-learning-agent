from unittest.mock import MagicMock
from langchain_core.messages import HumanMessage
from user_profile.schema import UserProfile, VideoInfo, SearchParams
from agents.scorer import scorer

if __name__ == "__main__":
    # Plausible user profile — French learner
    mock_profile_fr = UserProfile(
        interests=["cinema", "history", "gastronomy"],
        dislikes=["reality TV", "sports"],
        languages=["English", "French"],
        language_levels={"English": "C2", "French": "A2"},
        saved_channels_id=["UCcinema123", "UChistoire456"],
        channel_ratings={
            "UCcinema123": 5.0,   # highly rated French cinema channel
            "UCreality789": 1.0   # poorly rated reality TV channel
        },
        video_ratings={
            "vid_easy_french": 5.0,   # loved easy French content
            "vid_hard_debate": 1.0    # hated complex French political debate
        }
    )

    # Mock store
    mock_memory_fr = MagicMock()
    mock_memory_fr.value = mock_profile_fr.model_dump()
    store_fr = MagicMock()
    store_fr.search.return_value = [mock_memory_fr]

    # Videos with different expected scores
    mock_videos_fr = [
        VideoInfo(
            video_id="3gmJXVqwiHQ",
            title=" 8 films pour améliorer ton français ",
            channel_id="UCcinema123",  # highly rated saved channel
            channel_title="Cinéma Facile",
            CC=True,
            published_time="1 month ago",
            views=85000,
            detected_language="French",
            detected_level="A2",      # perfect level match
            for_students=True,
            score=None
            # expected score: HIGHEST — cinema interest, saved channel,
            # perfect level, for students, CC available
        ),
        VideoInfo(
            video_id="Au7DPVUpc6A",
            title="La Révolution Française de 1789 à 1792 ",
            channel_id="UChistoire456",  # saved channel
            channel_title="Histoire Vivante",
            CC=True,
            published_time="3 months ago",
            views=120000,
            detected_language="French",
            detected_level="B1",      # slightly above target A2
            for_students=False,
            score=None
            # expected score: HIGH — history interest, saved channel
            # slight penalty for being above target level
        ),
        VideoInfo(
            video_id="Xu-FLmk7t5Y",
            title=" LA CUISINE FRANCAISE : C'EST SACRÉ ! ",
            channel_id="UCfood999",
            channel_title="Cuisine Française",
            CC=True,
            published_time="2 weeks ago",
            views=67000,
            detected_language="French",
            detected_level="A2",      # perfect level match
            for_students=False,
            score=None
            # expected score: MEDIUM-HIGH — gastronomy interest, right level
            # unknown channel, no ratings
        ),
        VideoInfo(
            video_id="dp4I9DIK_pk",
            title="Présidentielle 2022 : le débat entre Macron et Le Pen résumé en 6 minutes",
            channel_id="UCnews777",
            channel_title="France Info",
            CC=False,
            published_time="1 week ago",
            views=450000,
            detected_language="French",
            detected_level="C1",      # way above target
            for_students=False,
            score=None
            # expected score: LOW — not in interests, way above level,
            # no CC, not for students
        ),
        VideoInfo(
            video_id="2e7DAdOyb10",
            title="BAGARRES et INSULTES 😤 Les meilleurs moments ! | LES ANGES | COMPILATION",
            channel_id="UCreality789",  # poorly rated channel
            channel_title="Reality France",
            CC=False,
            published_time="2 days ago",
            views=1500000,
            detected_language="French",
            detected_level="B2",      # above target
            for_students=False,
            score=None
            # expected score: LOWEST — reality TV (disliked), poorly rated channel,
            # above level, no CC
        ),
    ]

    config_fr = {"configurable": {"user_id": "test_user_fr"}}

    state_fr = {
        "messages": [HumanMessage(content="Find me French cinema videos at A2")],
        "search_params": SearchParams(
            topic="cinema",
            language="fr",
            target_level="A2",
            max_results=10
        ),
        "videos": mock_videos_fr,
    }

    results = scorer(state_fr, config_fr, store_fr)

    for r in results["videos"]:
        print(f"Video title: {r.title}")
        print(f"Score: {r.score}")
        print(f"Score explanation: {r.score_explanation}")
        print("================")