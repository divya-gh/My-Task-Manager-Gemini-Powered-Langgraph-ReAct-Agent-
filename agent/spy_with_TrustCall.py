
from trustcall import create_extractor
from langchain_core.messages import AIMessage , HumanMessage , SystemMessage
from agent.LLM import llm
from agent.schemas import UserProfile, ToDo

#trustcall to extract profile information
profile_extractor = create_extractor(llm,
                                       tools=[UserProfile],
                                       tool_choice='UserProfile',
                                      )


# define spy class
# Inspect the tool calls made by Trustcall
class Spy:
    def __init__(self):
        self.called_tools = []

    def __call__(self, run):
        # Collect information about the tool calls made by the extractor.
        q = [run]
        while q:
            r = q.pop()
            if r.child_runs:
                q.extend(r.child_runs)
            if r.run_type == "chat_model":
                self.called_tools.append(
                    r.outputs["generations"][0][0]["message"]["kwargs"]["tool_calls"]

                )
# instantiate spy
spy = Spy()

# create turstcall extractor to extract  todo list
trustcall_todo = create_extractor(llm,
                                  tools=[ToDo],
                                  tool_choice="ToDo",
                                  enable_inserts=True,
                                  enable_updates=True,
                                  ).with_listeners(on_end=spy)


