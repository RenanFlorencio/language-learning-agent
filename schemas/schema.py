from typing import Annotated, Optional, Literal
from pydantic import BaseModel, ConfigDict, PositiveInt, Field
from langgraph.graph import MessagesState


class SearchParams(BaseModel):
    """Represents the parameters for searching videos based on user preferences.
    Attributes:
        topic (str): The topic or subject matter the user is interested in, e.g., "machine learning", "cooking recipes", "travel vlogs".
        language (str): The language in which the user wants to find videos, e.g., "English", "Spanish", "French".
        target_level (str): The language proficiency level the user is targeting, e.g., "A1", "A2", "B1", "B2", "C1", "C2".
        max_results (PositiveInt): The maximum number of video results to return, must be a positive integer.   
    """
    topic: str 
    language: str 
    target_level: str
    max_results: PositiveInt = 10

class NewsSearchParams(BaseModel):
    """Represents the parameters for searching news articles based on user preferences.
    Attributes:
        topic (str): The topic or subject matter the user is interested in, e.g., "climate change", "technology advancements", "sports news".
        language (str): The language in which the user wants to find news articles, e.g., "en" for English, "es" for Spanish, "fr" for French.
        from_date (str): The start date for the news articles in the format "YYYY-MM-DD", e.g., "2023-01-01".
        to_date (str): The end date for the news articles in the format "YYYY-MM-DD", e.g., "2023-12-31".
        sources (str | None): A comma-separated string of news sources to filter the articles, e.g., "bbc-news,the-verge". 
            If None, articles from all sources will be included.
        max_results (PositiveInt): The maximum number of news article results to return, must be a positive integer. Default is 10.  
    """
    topic: str | None = None
    language: str
    from_date: str | None = None
    to_date: str | None = None
    sources: str | None = None
    max_results: PositiveInt = 10

class NewsArticle(BaseModel):
    """Represents a news article with relevant metadata.
    Attributes:
        title (str): The title of the news article.
        source (str): The source or publisher of the news article, e.g., "BBC News", "The Verge".
        published_at (str): The publication date of the news article in the format "YYYY-MM-DD", e.g., "2023-01-15".
        url (str): The URL link to the full news article.
    """
    title: str
    author: str | None = None
    description: str | None = None
    source: str
    published_at: str
    url: str
    

class UserProfile(BaseModel):
    """ Represents the user's profile containing their preferences and information relevant to video recommendations.
    Attributes:
        video_interests (list[str] | []): A list of video topics the user is interested in, e.g., "technology", "cooking", "travel". Can be [] if not set.
        video_dislikes (list[str] | []): A list of video topics the user dislikes, e.g., "politics", "sports", "reality TV". Can be [] if not set.
        news_interests (list[str] | []): A list of news topics the user is interested in, e.g., "politics", "economy", "sports". Can be [] if not set.
        news_dislikes (list[str] | []): A list of news topics the user dislikes, e.g., "fake news", "sensationalism". Can be [] if not set.
        languages (list[str] | []): A list of languages the user is proficient in, e.g., "English", "Spanish", "French". Can be [] if not set.
        language_levels (dict[str, str] | {}): A mapping of language to proficiency level, e.g., {"English": "B2", "Spanish": "C1"}. Can be {} if not set.
        saved_channels_id (list[str] | []): A list of channel IDs that the user has saved or subscribed to. Can be [] if not set.
        channel_ratings (dict[str, Annotated[float, Field(ge=0, le=5)]] | {}): A mapping of channel ID to a rating from 0 to 5, where 0 means the user dislikes the channel and 5 means the user loves the channel. Can be {} if not set.
        video_ratings (dict[str, Annotated[float, Field(ge=0, le=5)]] | {}): A mapping of video ID to a rating from 0 to 5, where 0 means the user dislikes the video and 5 means the user loves the video. Can be {} if not set.   
        """
    # Video preferences
    video_interests: list[str] = []
    video_dislikes: list[str] = []

    # News preferences
    news_interests: list[str] = []
    news_dislikes: list[str] = []

    # Shared
    languages: list[str] = []
    language_levels: dict[str, str] = {}
    prefered_news_sources: list[str] = []
    saved_channels_id: list[str] = []
    channel_ratings: dict[str, Annotated[float, Field(ge=0, le=5)]] = {}
    video_ratings: dict[str, Annotated[float, Field(ge=0, le=5)]] = {}


class TranscriptAnalysis(BaseModel):
    level_explanation: str
    detected_language: str | None = None
    detected_level: str | None = None
    for_students: bool | None = None


class ScoreAnalysis(BaseModel):
    score_explanation: str
    score: Annotated[int, Field(ge=0, le=100)]


class VideoInfo(BaseModel):
    """
    Represents metadata information about a video.

    Attributes:
        video_id (str): Unique identifier for the video.
        title (str): The title of the video.
        channel_id (str): Unique identifier for the channel that uploaded the video.
        channel_title (str): The name of the channel that uploaded the video.
        CC (bool): Indicates whether the video has closed captions available.
        detected_language (str | None): The language detected in the video content, or None if not detected.
        detected_level (str | None): The language proficiency level detected in the video content, or None if not detected.
        for_students (bool | None): Indicates whether the video is suitable for students, or None if not determined.
        score (float | None): A score representing the relevance or quality of the video, or None if not scored. Default is -1, indicating that the video has not been scored yet.
    """
    model_config = ConfigDict(frozen=False)
    video_id: str # Provided by Search Agent
    title: str # Provided by Search Agent
    channel_id: str # Provided by Search Agent
    channel_title: str # Provided by Search Agent
    CC: bool # Provided by Search Agent (Closed Captions)
    published_time: str # Provided by Search Agent
    views: int # Provided by Search Agent
    detected_language: str | None = None # Detected by Transcription Agent
    detected_level: str | None = None # Detected by Transcription Agent
    level_explanation: str | None = None # Explanation of how the detected level was determined based on transcript content, provided by Transcription Agent
    for_students: bool | None = None # Determined by Transcription Agent based on content suitability for students
    score_explanation: str | None = None # Explanation of how the score was calculated based on relevance and user preferences, provided by Scoring Agent
    score : Annotated[int, Field(ge=0, le=100)] | None = None # Calculated by Scoring Agent, None if not yet scored

# This is going to be the state that is passed around in the orchestrator agent
class State(MessagesState):
    search_params: Optional[SearchParams]
    news_search_params: Optional[NewsSearchParams]
    videos: Optional[list[VideoInfo]]
    news: Optional[list[NewsArticle]]
    video_id : Optional[str] # The video id of the video being processed in the current step, used for transcript and scoring agents

class ExecuteIntent(BaseModel):
    """Call this to execute the user's intent"""
    intent: Literal[
        "full_search",
        "transcript_only", 
        "rerank_only",
        "profile_update",
        "out_of_scope"
    ]
    search_params: SearchParams | None = None
    news_search_params : NewsSearchParams | None = None
    video_id: str | None = None