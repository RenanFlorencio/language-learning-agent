import json
from agents.shared import USE_MOCK_DATA
from tests.fixtures import mock_transcripts
from youtube_transcript_api import Transcript, YouTubeTranscriptApi
from langchain_core.tools import tool
from pathlib import Path

ytt_api = YouTubeTranscriptApi()
MAX_SNIPPETS = 50

# Based on https://github.com/jdepoix/youtube-transcript-api

def api_call(video_id: str, languages: list[str]) -> Transcript:
    """Fetches the transcript for a given YouTube video ID in the specified languages.
    Args:
        video_id (str): The unique identifier for the YouTube video
        languages (list[str]): A list of language codes (e.g., ["de", "es"]) it will first try to fetch the german transcript ('de') and then fetch the english transcript ('en') if it fails to do so.
    Returns:
        tuple[str, str]: A tuple containing the language code and a single concatenated string containing the text of the transcript. For example:
        ("de", "Hello, welcome to this video. In this video, we will discuss...")
    """
    try: 
        transcript_list = ytt_api.list(video_id)
        transcript = transcript_list.find_transcript(languages)
        return transcript
    
    except Exception as e:
        raise Exception(f"Could not fetch transcript... Error: {e}")


def get_transcript(video_id: str, languages: list[str]) -> tuple[str, str]:
    """Fetches the transcript for a given YouTube video ID in the specified languages and returns it as a single concatenated string.
    Args:
        video_id (str): The unique identifier for the YouTube video
        languages (list[str]): A list of language codes (e.g., ["de", "es"]) it will first try to fetch the german transcript ('de') and then fetch the english transcript ('en') if it fails to do so.
    Returns:
        tuple[str, str]: A tuple containing the transcript str and the language code. For example:
        ("Bonjour. Aujourd'hui on va parler des...", "fr")
    """
    if USE_MOCK_DATA:
        return (str(mock_transcripts.get(video_id)), "")

    cached_file = Path(f"cache/transcript/{video_id}.json")
    cached_file.parent.mkdir(parents=True, exist_ok=True)  # add this line to ensure the directory exists

    if cached_file.exists():
        return json.loads(cached_file.read_text())

    transcript = api_call(video_id, languages)
    str_snippets = transcript.fetch()[:MAX_SNIPPETS]
    concat_str = " ".join([snippet.text for snippet in str_snippets])

    language_code = transcript.language_code

    # Cache the transcript for future use
    cached_file.write_text(json.dumps((concat_str, language_code)))
    return concat_str, language_code
