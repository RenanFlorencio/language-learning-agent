from user_profile.schema import State
from prompts import orchestrator_prompt
from agents.shared import get_user_profile, get_model
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from user_profile.schema import ExecuteIntent
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
    
    if response.tool_calls:
        print("Orchestrator made tool call!")
        args = response.tool_calls[0]["args"]  # reading what LLM generated
        print(f"tool call args: {args}")
        search_params = args.get("search_params", None)  # getting the specific field
        if search_params and len(search_params["language"]) > 2:
            return {
                "messages": [HumanMessage(content="Please use a language code (e.g. 'de', 'fr') not the full language name")],
                "search_params": None,
                "video_id": None
            }
        video_id = args.get("video_id", None)
    else:
        search_params = None
        video_id = None

    return {"messages" : [response], "search_params": search_params, "video_id" : video_id}