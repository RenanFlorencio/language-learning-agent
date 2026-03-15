from user_profile.schema import State
from prompts import profile_prompt
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from user_profile.schema import UserProfile
from langchain_core.messages import SystemMessage, merge_message_runs, AIMessage
from trustcall import create_extractor
from agents.shared import get_model
import uuid
import configuration


def profile_updater(state : State, config : RunnableConfig, store : BaseStore):
    # This agent is responsible for updating the user's profile based on their interactions and feedback.
    configurable = configuration.Configuration.from_runnable_config(config)
    user_id = configurable.user_id
    namespace = ("profile", user_id)
    existing_items = store.search(namespace)
    model = get_model()

    # Format the existing memories for the Trustcall extractor
    tool_name = "UserProfile"
    existing_memories = ([(existing_item.key, tool_name, existing_item.value)
                          for existing_item in existing_items]
                          if existing_items
                          else None
                        )
    
    updated_messages=list(merge_message_runs(messages=[SystemMessage(content=profile_prompt.PROMPT)] + state["messages"][-3:-1]))
    # Create the Trustcall extractor for updating the user profile 
    profile_extractor = create_extractor(
        model,
        tools=[UserProfile],
        tool_choice=tool_name,
    )

    # This might return several updates if the message has several updates
    result = profile_extractor.invoke({"messages": updated_messages, 
                                         "existing": existing_memories}) 

    # Save the memories from Trustcall to the store
    for r, rmeta in zip(result["responses"], result["response_metadata"]):
        store.put(
            namespace,                              # ("profile", user_id) — where to store
            rmeta.get("json_doc_id", str(uuid.uuid4())),  # key — reuses existing doc id if updating
            r.model_dump(mode="json"),             # value — the updated UserProfile as dict
        )

    last_message = state['messages'][-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError("Expected AIMessage with tool calls")
    tool_calls = last_message.tool_calls

    return {"messages": [{"role": "tool", "content": "updated profile", "tool_call_id":tool_calls[0]['id']}]}