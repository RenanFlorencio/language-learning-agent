from user_profile.schema import State
from prompts import transcript_prompt
from agents.shared import get_model, USE_MOCK_DATA, parse_search_params
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from user_profile.schema import TranscriptAnalysis
from langchain_core.messages import SystemMessage
from tools import youtube_transcript
from tqdm import tqdm
from typing import cast
from tests.fixtures import mock_transcripts

def transcripter(state : State, config : RunnableConfig, store : BaseStore):
    # This agent is responsible for generating transcripts for videos that are found to be relevant to the user's preferences.
    model = get_model()
    if not state["videos"]:
        return {"transcripts": None}
    
    # Get the search parameters from state
    raw_search_params = state["search_params"]
    search_params = parse_search_params(raw_search_params)
    assert search_params is not None, "search_params should not be None in search_agent" 
    
    language = search_params.language
    videos = state["videos"]

    for v in tqdm(videos, desc="Extracting information from transcripts", unit="video"):
        
        if USE_MOCK_DATA:
            transcript = mock_transcripts.get(v.video_id, None)
        else:
            try:
                transcript, _ = youtube_transcript.get_transcript(v.video_id, [language])
            except Exception as e:
                print(f"Could not fetch transcript for video {v.video_id}... Error: {e}")
                transcript, _ = None, None

        detected_information = cast(TranscriptAnalysis, model.with_structured_output(TranscriptAnalysis).invoke(
                [SystemMessage(content=transcript_prompt.PROMPT.format(transcript=transcript))] 
        ))
        v.level_explanation = detected_information.level_explanation
        v.detected_language = detected_information.detected_language
        v.detected_level = detected_information.detected_level
        v.for_students = detected_information.for_students

    return {"videos": videos}