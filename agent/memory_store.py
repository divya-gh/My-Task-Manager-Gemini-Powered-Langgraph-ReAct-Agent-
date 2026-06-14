# set checkpointer and long term memory
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

session_memory = MemorySaver()
store_memory = InMemoryStore()