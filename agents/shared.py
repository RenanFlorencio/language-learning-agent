from langchain_deepseek import ChatDeepSeek
import os
from dotenv import load_dotenv
from schemas.schema import SearchParams, NewsSearchParams

load_dotenv()
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
if USE_MOCK_DATA:
    print("USING MOCK DATA FOR TESTING")

USE_MOCK_NEWS = os.getenv("USE_MOCK_NEWS", "false").lower() == "true"
if USE_MOCK_NEWS:
    print("USING MOCK NEWS FOR TESTING")

def get_user_profile(user_id: str, store) -> dict | None:
    namespace = ("profile", user_id)
    memories = store.search(namespace)
    return memories[0].value if memories else None

def get_model():
    return ChatDeepSeek(model="deepseek-chat", temperature=0.5)


def parse_search_params(raw: dict | SearchParams | None) -> SearchParams | None:
    if raw is None:
        return None
    if isinstance(raw, dict):
        return SearchParams(**raw)
    return raw

def parse_news_search_params(raw : dict | NewsSearchParams | None) -> NewsSearchParams | None:
    if raw is None:
        return None
    if isinstance(raw, dict):
        return NewsSearchParams(**raw)
    return raw