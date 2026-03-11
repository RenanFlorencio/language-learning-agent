from typing import Annotated, Optional
from langgraph.graph import MessagesState
from pydantic import BaseModel, PositiveInt, Field
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
    max_results: PositiveInt

class UserProfile(BaseModel):
    """ Represents the user's profile containing their preferences and information relevant to video recommendations.
    Attributes:
        interests (list[str] | []): A list of topics the user is interested in, e.g., "technology", "cooking", "travel". Can be [] if not set.
        dislikes (list[str] | []): A list of topics the user dislikes, e.g., "politics", "sports", "reality TV". Can be [] if not set.
        languages (list[str] | []): A list of languages the user is proficient in, e.g., "English", "Spanish", "French". Can be [] if not set.
        language_levels (dict[str, str] | {}): A mapping of language to proficiency level, e.g., {"English": "B2", "Spanish": "C1"}. Can be {} if not set.
        saved_channels_id (list[str] | []): A list of channel IDs that the user has saved or subscribed to. Can be [] if not set.
        channel_ratings (dict[str, Annotated[float, Field(ge=0, le=5)]] | {}): A mapping of channel ID to a rating from 0 to 5, where 0 means the user dislikes the channel and 5 means the user loves the channel. Can be {} if not set.
        video_ratings (dict[str, Annotated[float, Field(ge=0, le=5)]] | {}): A mapping of video ID to a rating from 0 to 5, where 0 means the user dislikes the video and 5 means the user loves the video. Can be {} if not set.   
        """

    interests: list[str] = []
    dislikes: list[str] = []
    languages: list[str] = []
    language_levels: dict[str, str] = {}
    saved_channels_id: list[str] = []
    channel_ratings: dict[str, Annotated[float, Field(ge=0, le=5)]] = {}
    video_ratings: dict[str, Annotated[float, Field(ge=0, le=5)]] = {}

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
    video_id: str # Provided by Search Agent
    title: str # Provided by Search Agent
    channel_id: str # Provided by Search Agent
    channel_title: str # Provided by Search Agent
    CC: bool # Provided by Search Agent (Closed Captions)
    published_time: str # Provided by Search Agent
    views: int # Provided by Search Agent
    detected_language: str | None = None # Detected by Transcription Agent
    detected_level: str | None = None # Detected by Transcription Agent
    for_students: bool | None = None # Determined by Transcription Agent based on content suitability for students
    score : Annotated[float, Field(ge=0, le=10)] | None = None # Calculated by Scoring Agent, None if not yet scored

# This is going to be the state that is passed around in the orchestrator agent
class State(MessagesState):
    search_params: Optional[SearchParams]
    videos: Optional[list[VideoInfo]]