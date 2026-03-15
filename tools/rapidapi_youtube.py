import requests
import os
from user_profile.schema import VideoInfo
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

def search_youtube_mock(topic: str, language: str, target_level: str) -> list[VideoInfo]:
    """Searches YouTube for videos matching the query, language, and region, and returns a list of VideoInfo objects containing metadata about the videos.
    Args:        
        query (str): The search query or keywords to find relevant videos, e.g., "beginner Spanish lessons", "cooking tutorials", "technology reviews".
        language (str): The language in which the user wants to find videos, e.g., "English", "Spanish", "French".
        max_results (int): The maximum number of results to return. Must be a positive integer.
    Returns:
        list[VideoInfo]: A list of VideoInfo objects containing metadata about the videos that match the search criteria, such as video ID, title, channel information, closed captions availability, published time, and placeholders for detected language, detected level, suitability for students, and score.
    """
    # Predefined list of video information for testing purposes
    mock_videos = [
        VideoInfo(
            video_id="video1",
            title="Beginner Spanish Lessons - Part 1",
            channel_id="channel1",
            channel_title="Spanish Learning Channel",
            CC=True,
            published_time="2 weeks ago",
            views=10000
        ),
        VideoInfo(
            video_id="video2",
            title="Intermediate Spanish Grammar - Part 1",
            channel_id="channel1",
            channel_title="Spanish Learning Channel",
            CC=False,
            published_time="1 month ago",
            views=5000
        )
    ]
    return mock_videos