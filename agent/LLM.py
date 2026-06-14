import os
from dotenv import load_dotenv
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict , Literal , Optional


load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_USE_V1"] = "true"

# create genai client and llm
client = genai.Client(api_key = os.environ["GOOGLE_API_KEY"])

# create a llm using any of the above models
llm = ChatGoogleGenerativeAI( model= "gemini-3.1-flash-lite-preview" , 
                              temperature = 0.2 )

llm.invoke("What day is this?").content

# 1. define a router class to select type of memory to update in the function
class Updatememory(TypedDict):
    update_type : Literal['update_profile', 'todo_update', 'update_instruction']


# bind the class a stool to LLM
llm_with_tool = llm.bind_tools([Updatememory])