from schemas.schema import State
from prompts import transcript_prompt
from agents.shared import get_model, parse_transcript_params
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from schemas.schema import TranscriptAnalysis
from langchain_core.messages import SystemMessage
from tools import youtube_transcript
from tqdm import tqdm
from typing import cast

def transcripter(state : State, config : RunnableConfig, store : BaseStore):
    # This agent is responsible for generating transcripts for videos that are found to be relevant to the user's preferences.
    model = get_model()
    if not state["videos"]:
        return {"transcripts": None}
    
    # Get the search parameters from state
    raw_transcript_params = state["transcript_params"]
    search_params = parse_transcript_params(raw_transcript_params)
    assert search_params is not None, "transcript_params should not be None in transcripter agent. Language needed." 
    
    language = search_params.language
    videos = state["videos"]

    for v in tqdm(videos, desc="Extracting information from transcripts", unit="video"):
        
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