from schemas.schema import State
from prompts import video_score_prompt
from agents.shared import get_user_profile, get_model
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from schemas.schema import ScoreAnalysis
from langchain_core.messages import SystemMessage
from tqdm import tqdm
from typing import cast
import configuration

def scorer(state: State, config: RunnableConfig, store: BaseStore) -> dict:
    configurable = configuration.Configuration.from_runnable_config(config)
    user_id = configurable.user_id
    user_profile = get_user_profile(user_id, store)
    videos = state['videos']
    model = get_model()
    
    if videos is None:
        print("No videos found for scoring.")
        return {"videos": []}
    
    for video in tqdm(videos, desc="Scoring videos", unit="video"):
        system_msg = video_score_prompt.PROMPT.format(
            user_profile=user_profile,
            video_info=video,
            search_params=state["search_params"],
        )
        model_score = cast(ScoreAnalysis, 
                           model.with_structured_output(ScoreAnalysis).invoke(
                            [SystemMessage(content=system_msg)])
        )
        print(f"Video ID: {video.video_id} - Score: {model_score.score} - Explanation: {model_score.score_explanation}")
        video.score_explanation = model_score.score_explanation
        video.score = model_score.score
    
    videos.sort(key=lambda x: x.score or 0, reverse=True)
    return {"videos": videos}