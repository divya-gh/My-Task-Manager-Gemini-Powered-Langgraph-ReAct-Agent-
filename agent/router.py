

from typing import Literal
from langgraph.graph import END
from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState 

# define router node
def router(state:MessagesState , config: RunnableConfig , store:BaseStore)->str:
    ''' based on the tool call route the workflow to proper node'''

    # get tool message
    tool_message = state['messages'][-1]    
    #print("Tool Call: ",tool_message)

    if len(tool_message.tool_calls)== 0:
        return END
    else:
        # get tool calls
        tool_calls = tool_message.tool_calls[0]
        if tool_calls['args']['update_type'] == 'update_profile':
            return 'update_profile'
        elif tool_calls['args']['update_type'] == 'todo_update':
            return 'todo_update'
        elif tool_calls['args']['update_type'] == 'update_instruction':
            return 'update_instruction'
        else:
            raise ValueError     