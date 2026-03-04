from youtube_transcript_api import Transcript, YouTubeTranscriptApi
from langchain_core.tools import tool

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

@tool
def get_transcript(video_id: str, languages: list[str]) -> tuple[str, str]:
    """Fetches the transcript for a given YouTube video ID in the specified languages and returns it as a single concatenated string.
    Args:
        video_id (str): The unique identifier for the YouTube video
        languages (list[str]): A list of language codes (e.g., ["de", "es"]) it will first try to fetch the german transcript ('de') and then fetch the english transcript ('en') if it fails to do so.
    Returns:
        tuple[str, str]: A tuple containing the language code and a single concatenated string containing the text of the transcript. For example:
        ("de", "Hello, welcome to this video. In this video, we will discuss...")
    """
    transcript = api_call(video_id, languages)
    str_snippets = transcript.fetch()[:MAX_SNIPPETS]
    concat_str = " ".join([snippet.text for snippet in str_snippets])

    language_code = transcript.language_code
    return language_code, concat_str
