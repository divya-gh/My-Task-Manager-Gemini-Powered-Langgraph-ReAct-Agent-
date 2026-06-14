
from langgraph.graph import MessagesState 
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from agent.LLM import llm , llm_with_tool
import uuid
from langchain_core.messages import AIMessage, HumanMessage , SystemMessage
from agent.spy_with_TrustCall import profile_extractor , trustcall_todo , spy
from agent.spy_toolcall_info import extract_tool_info
from agent.schemas import LLM_Instructions




# set up instructions

llm_instruction = """ You are a helpful React agent assistant with memory who responds proffesionaly to the user and assists him with managing the task and todo list.
                        You have the memory of previous interactions, semantic memory of user as user profile, todo list (containing ongoing, completed or 
                        yet to complete with dedalines), memories of instructions on task completion (either given by the user or self updated).

                        Here are your memories(May be empty sometimes):
                        Profile Memory: <user_profile>{profile_memory}</user_profile>\n
                        Todo Memory: <ToDo>{todo_memory}</ToDo>\n
                        Instruction Memory: <instructions>{intructions_memory}</instructions>\n

                        You will be given chat messges below. Follow these instruction before responding to the user:
                        - Use the given memories to personalize your response
                        - Based on the following instruction, decide weather any long term memory needs to be updated:
                            1. If personal or semantic facts are given[likes, loves, intrests, wants, desires etc], update the user profile by calling 
                                'Updatememory' tool with the 'update_type' as 'update_profile'.
                            2. If todo , plan or tasks are mentioned, update the todo list by calling 'Updatememory' tool with the 'update_type' as 'todo_update'.
                            3. if instructions are given or mentioned, update the intructions by calling 
                                'Updatememory' tool with the 'update_type' as 'update_instruction'.
                        - use your react skills to reflect on HumanMessage and memories again to re call the tool `Updatememory` 
                        with update type 'update_profile' , 'todo_update' or 'update_instruction' to update any missing information. 
                        - Update or inform the user about memory update only if it is related to or about the `todo list`. Do not talk about profile or instructions used.
                        - Do not perform parallel tool calling. Only call one tool at a time
                        -  Do not omit information, hallucinate or invent information while updating the memory or responding to the user.
                        - go through the HumanMessages again to see if all the user information is updated in the memory. do not miss any facts or interests.
                        - Be therough , helpful and natural
                        Instruction to respond to the user:
                        1. Reflect on the chat messages and ensure you have called the tool for all types as per user request or instructions. 
                        2. Keep in mind that sometimes memory can be None if no information were stored 
                        3. sometimesyou have to make sure all the tools are called (Example: user may want tou to update all the mwmories profile , 
                        instructions and todo list. If you see any memory is missing facts mentioned by the user
                        call the appropriate tool with their 'update_type'.
                        2. If you are done with all the tool call types,  generate a final answer in the format : `AI_response:` , which is a response to the user
                        3. If you have generated a `AI_response:`, END the conversation .
                        """


def LLM_chatbot(state:MessagesState , config: RunnableConfig , store:BaseStore):
    ''' chat function that retrives all the memory and personalizes the response'''

    # set store memory configuratons for retrival
    user_id = str(config['configurable']['user_id'])
    key = uuid.uuid4()

    # get user profile memory
    tool_name_P = 'UserProfile'
    namespace_prfl = (tool_name_P , user_id)  

    # get existing memory of user profile
    existing_profile = store.search(namespace_prfl)
    #print(existing_profile)
    # extract content
    if existing_profile:
        profile_content = existing_profile[0].value
    else:
        profile_content = None

    # get todo list memory
    tool_name_todo = 'ToDo'
    namespace_todo = (tool_name_todo , user_id)  

    # get existing memory of user todo list
    existing_todo = store.search(namespace_todo)
    #print(existing_todo)
    # extract content
    if existing_todo:
        todo_content = existing_todo[0].value
    else:
        todo_content = None

    # get instruction memory
    memory_name_instr = 'Instructions'
    namespace_instr = (memory_name_instr , user_id)  

    # get existing memory of user todo list
    existing_instr = store.search(namespace_instr)
    #print(existing_instr)
    # extract content
    if existing_instr:
        instr_content = existing_instr[0].value
    else:
        instr_content = None

    # set system instruction
    llm_sys_instr = SystemMessage(content=llm_instruction.format(profile_memory = profile_content , todo_memory= todo_content , intructions_memory= instr_content))

    response = llm_with_tool.invoke([llm_sys_instr] + state['messages'])
    #print(f"LLM Response: {response}")

    # route AI message
    if response.tool_calls:
        return {'messages': [response]}
    else:
        final_answer = AIMessage(content=response.content[0]['text'] , Role = 'AI' )
        #print("Final Answer: ", final_answer)
        return {'messages': [final_answer]}


# define the update profile node
from datetime import datetime
from langchain_core.messages import merge_message_runs , HumanMessage , SystemMessage, ToolMessage


# set up trustcall instructions:

trustcall_profile_instr = """
Your task is to extract and maintain an accurate user profile based on the 
conversation provided to you. You will also be given the existing profile 
memory(memory may be empty sometimes). Your job is to update, refine, or extend this memory as needed.

Follow these rules carefully:
1. Extract all the field values if mentioned by the user:
    - name
    - age
    - relations
    - interests
    - job
    - location
    - any other required field

1. Use the available memory tools to store any new or updated profile details 
   about the user. Do not lose or overwrite existing information unless the 
   conversation clearly provides a correction.

2. When multiple updates or insertions are required, use parallel tool calls 
   so that all profile changes are handled efficiently and simultaneously.

3. Consider the current date and time when interpreting time‑sensitive 
   information. Current system time: {time}

4. Only extract information that is explicitly stated or strongly implied 
   by the user. Do not invent or assume details.

5. Ensure the resulting profile is clean, structured, and reflects the 
   most up‑to‑date understanding of the user.
"""




def update_profile(state:MessagesState , config:RunnableConfig , store:BaseStore):
    ''' updates and/or creates user profile while reflecting on and retaining existing memory'''

    # set configueration
    user_id = str(config['configurable']['user_id'])
    tool_name = "UserProfile"
    namespace = (tool_name , user_id)

    # get memory
    exiting_profile = store.search(namespace)

    # get content list of tuple
    exiting_profile_content = [(item.key , tool_name , item.value) for item in exiting_profile]if exiting_profile else None

    # set systm instruction for Trustcall extracor
    trustcall_sys_instr = SystemMessage(content=trustcall_profile_instr.format(time = datetime.now().isoformat()))

    # merge messages for structured trustcall input . avoid last AI update from llm which was just updated
    merged_messages = list(merge_message_runs(messages=[trustcall_sys_instr] + state["messages"]))

    # invoke extractor
    result = profile_extractor.invoke({'messages' : merged_messages,
                                      'existing' : exiting_profile_content })
    # save memory in the store
    for i , content in enumerate(result['responses']):
        # json patch id if updated or uuid if new memory is created
        key = result['response_metadata'][i].get('json_doc_id' , str(uuid.uuid4()))
        store.put(namespace , key , content.model_dump(mode='json'))

    # update tool message
    id = state['messages'][-1].tool_calls[0]['id']
    return {'messages' : [ToolMessage(content = "Profile Memory updated" , Role = "Tool" , tool_call_id = id)]}         

trustcall_todo_instr = """
Your task is to extract, create, and update the user's ToDo items based on the 
conversation. You will also be given the existing ToDo memory. Your job is to 
add new tasks, update existing ones, or refine details such as deadlines, 
status, reminders, and instructions.

Follow these rules carefully:

1. Use the provided memory tools to store any new or updated ToDo items. 
   Preserve existing tasks unless the user clearly modifies or corrects them.

2. When multiple tasks or updates are required, use parallel tool calls so 
   all ToDo changes are handled efficiently and simultaneously.

3. Consider the current date and time when interpreting deadlines, reminders, 
   or time‑sensitive instructions. Current system time: {time}

4. Extract only what the user explicitly states or strongly implies. Do not 
   invent tasks or deadlines.

5. Each ToDo item should be clean, structured, and include fields such as:
   - task
   - status
   - deadline (ISO format when possible)
   - instruction or description
   - reminder time (if applicable)
   - desired_solution (what needs to be done, remembered or taken care of to complete the task)

6. If the user expresses intent to remember something for later (e.g., 
   “remind me”, “don’t let me forget”), convert it into a ToDo item with an 
   appropriate reminder or deadline.
7. Important: If user asks for any help (e.g., asks for suggesion, uses 'Tell me, Let me know, what else needs to be done , Provide me solution' in the conversation), 
 convert it into a proper 'desired_solution'.
7. Ensure the final ToDo memory reflects the most accurate and up‑to‑date 
   understanding of the user's tasks and plans.
"""


def todo_update(state:MessagesState , config:RunnableConfig , store:BaseStore):
    ''' updates and/or creates todo list while reflecting on and retaining existing memory'''

    # set configueration
    user_id = str(config['configurable']['user_id'])
    tool_name = "ToDo"
    namespace = (tool_name , user_id)

    # get memory
    exiting_todo = store.search(namespace)

    # get content list of tuple
    exiting_todo_content = [(item.key , tool_name , item.value) for item in exiting_todo]if exiting_todo else None

    # set systm instruction for Trustcall extracor
    trustcall_sys_instr = SystemMessage(content=trustcall_todo_instr.format(time = datetime.now().isoformat()))

    # merge messages for structured trustcall input . avoid last AI update from llm which was just updated
    merged_messages = list(merge_message_runs(messages=[trustcall_sys_instr] + state["messages"]))

    # invoke extractor
    result = trustcall_todo.invoke({'messages' : merged_messages,
                                      'existing' : exiting_todo_content })
    #print("Todo_trustcal_result: ", result)
    #print("-"*40)

    # save memory in the store
    for content, rmd_id in zip(result['responses'], result['response_metadata']):
        # json patch id if updated or uuid if new memory is created
        key = rmd_id.get('json_doc_id' , str(uuid.uuid4()))
        store.put(namespace , key , content.model_dump(mode='json'))

    # update tool message
    id = state['messages'][-1].tool_calls[0]['id']
    tool_content = extract_tool_info(spy.called_tools , tool_name)
    return {'messages' : [ToolMessage(content = tool_content , role = "Tool" , tool_call_id = id)]}        



# define a node with sys instructions

generate_instr_LLM_prompt = ''' You are a proficient instructions generator who is capable of writing instructions on how to manage, 
                            update todo list items for the user. reflect on following instructions:
                            1. Use any instruction or information given by the user(they might tell you how they would like to the todo list to be added or updated).
                            2. Make it as easy as possible follow , manage and understand the list.
                            3. Use existing memory about the instructions given before.
                            4. Be proffessional and helpful. 
                            Here is the current instruction: <current_instructions>{instr}</current_instructions>'''



# create  a node
def update_instruction(state:MessagesState , config:RunnableConfig , store:BaseStore):
    ''' Node to generate or update instruction on how to manage , add , update todo list'''

    # set configerations for extracting memory
    user_id = str(config['configurable']['user_id'])
    memory_name = 'Instructions'
    namespace = (memory_name , user_id)
    key = "user_instruction"

    # get existing memory
    existing_instruction = store.search(namespace)

    # format to get value 
    existing_inst_content = [m.value for m in existing_instruction] if existing_instruction else None
    #print(f"Existing Instructions: {existing_inst_content}")

    # set sys instructions
    syst_instr_LLM = SystemMessage(content=generate_instr_LLM_prompt.format(instr = existing_inst_content))

    # call LLM
    human_msg = HumanMessage(content="update instructions based on the conversation")
    Response = llm.with_structured_output(LLM_Instructions).invoke([syst_instr_LLM] + state['messages'] +[human_msg])

    # save memory
    value = {'instruction_memory': Response.instructions }
    store.put(namespace , key , value)

    # update the state
    id = state['messages'][-1].tool_calls[0]['id']
    return {'messages': ToolMessage(content = "Instruction for todo list are updated." , role = "LLM" , tool_call_id = id)} 


