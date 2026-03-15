from langchain_deepseek import ChatDeepSeek
import os
from dotenv import load_dotenv
from user_profile.schema import SearchParams

load_dotenv()
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
if USE_MOCK_DATA:
    print("USING MOCK DATA FOR TESTING")

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