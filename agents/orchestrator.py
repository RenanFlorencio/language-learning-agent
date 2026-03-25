from schemas.schema import State
from prompts import orchestrator_prompt
from agents.shared import get_user_profile, get_model
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from schemas.schema import ExecuteIntent
from langchain_core.messages import HumanMessage, SystemMessage
import configuration

def orchestrator(state : State, config : RunnableConfig, store : BaseStore):
    
    # # Retrieve the user state from the store
    configurable = configuration.Configuration.from_runnable_config(config)
    user_id = configurable.user_id
    user_profile = get_user_profile(user_id, store)

    system_msg = orchestrator_prompt.PROMPT.format(user_profile=user_profile)

    model = get_model()
    response = model.bind_tools([ExecuteIntent]).invoke([SystemMessage(content=system_msg)] + state["messages"])
    
    search_params = None
    transcript_params = None
    news_search_params = None
    
    if response.tool_calls:
        print("Orchestrator made tool call!")
        args = response.tool_calls[0]["args"]  # reading what LLM generated
        print(f"tool call args: {args}")
        intent = args.get("intent", None)

        if intent == "youtube_search":
            search_params = args.get("search_params", None)  # getting the specific field
            if search_params and len(search_params["language"]) > 2:
                return {
                    "messages": [HumanMessage(content="Please use a language code (e.g. 'de', 'fr') not the full language name")],
                    "search_params": None,
                    "news_search_params": None,
                    "video_id": None
                }
            return {"messages" : [response], "search_params": search_params, "news_search_params": None, "video_id": None}

        elif intent == "transcript_only":
            transcript_params = args.get("transcript_params", None)  # getting the specific field

        elif intent == "news_search":
            news_search_params = args.get("news_search_params", None)  # getting the specific field
            if news_search_params and len(news_search_params["language"]) > 2:
                return {
                    "messages": [HumanMessage(content="Please use a language code (e.g. 'de', 'fr') not the full language name")],
                    "news_search_params": None,
                    "search_params": None,
                    "video_id": None
                }
        
    return {"messages" : [response], "search_params": search_params, "news_search_params": news_search_params, "transcript_params": transcript_params}