import requests
import os
from schemas.schema import VideoInfo
from agents.shared import USE_MOCK_DATA
from tests.fixtures import mock_videos
from dotenv import load_dotenv
from pathlib import Path
import json

MIN_LENGTH_SECONDS = 120
url = "https://youtube138.p.rapidapi.com/search/"

def api_call(query: str, language: list[str]) -> dict:
    """Makes an API call to the YouTube search endpoint using RapidAPI to retrieve video data based on the search query and language."""
    load_dotenv(override=True)

    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "youtube138.p.rapidapi.com",
        "q": query,
        "hl": language,
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"API call failed with status code {response.status_code}: {response.text}")
    
    return response.json()


def search_youtube(query: str, language: list[str], max_results: int) -> list[VideoInfo]:
    """Searches YouTube for videos matching the query, language, and region, and returns a list of VideoInfo objects containing metadata about the videos.
    Args:        
        query (str): The search query or keywords to find relevant videos, e.g., "beginner Spanish lessons", "cooking tutorials", "technology reviews".
        language (list[str]): The languages in which the user wants to find videos, e.g., ["English", "Spanish", "French"].
        max_results (int): The maximum number of results to return. Must be a positive integer.
    Returns:
        list[VideoInfo]: A list of VideoInfo objects containing metadata about the videos that match the search criteria, such as video ID, title, channel information, closed captions availability, published time, and placeholders for detected language, detected level, suitability for students, and score.
    """
    if USE_MOCK_DATA:
        return mock_videos

    # Try to hit the cache first to avoid unnecessary API calls
    cache_file = Path(f"cache/search/{query}_{language}.json")
    if cache_file.exists():
        return json.loads(cache_file.read_text())

    response = api_call(query, language)

    videos = []
    for item in response.get("contents", []):
        if len(videos) >= max_results:
            break

        if item["type"] == "video":
            if item["video"]["lengthSeconds"] < MIN_LENGTH_SECONDS: # Filter out videos shorter than 2 minutes
                continue

            video_info = VideoInfo(
                video_id=item["video"]["videoId"],
                title=item["video"]["title"],
                channel_id=item["video"]["author"]["channelId"],
                channel_title=item["video"]["author"]["title"],
                CC=True if "CC" in item["video"]["badges"] else False,
                published_time=item["video"]["publishedTimeText"],
                views=item["video"]["stats"]["views"]
            )
            videos.append(video_info)

    if len(videos) == 0:
        raise Exception("No videos found matching the search criteria.")
    
    # Cache the results for future use
    cache_file.write_text(json.dumps([v.model_dump() for v in videos]))
    return videos
