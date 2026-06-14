
# define classes for trustCall memory management for storing

from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime

# save user Profile in
class UserProfile(BaseModel):
    user_name: Optional[str] = Field(description="preferred name of the user", default='User')
    age: Optional[int] = Field(description="age of the user")
    location: Optional[str] = Field(description="where the user lives")
    job: Optional[str] = Field(description="The user's job", default=None)
    connections: List[str] = Field(description="Personal connection of the user, such as family members, friends, or coworkers",default_factory=List)
    interests:List[str] = Field(description= " List of user's preference, loves , likes, wants and interests that he mentions." , default_factory=List)


# save to_do list in
class ToDo(BaseModel):
    task: str = Field(description="task to be completed")
    time_taken: Optional[int] = Field(description="Estimated time to complete the task (Hours:Minutes)" , default = None )
    deadline: Optional[datetime] = Field(description= "Estimated deadline to complete the task. May be as specified by the user", default= None)
    instruction: Optional[str] =Field(description=""" ANy instruction provided by the user to complete the task.
                                                    Example: rules, specific ideas, service providers, websites or any
                                                    concrete options relevant to completing the task""", default = None)
    desired_solution:Optional[str] = Field(description="Any Information about how the final solution or output should look like" , default = None)
    status:Literal["not started", "in progress", "done", "archived"] = Field(description="Current status of the task", default="not started")



# 3. define instruction class for LLM to generate/modify instructions
# generate structred output
class LLM_Instructions(BaseModel):
    instructions: str = Field(description="Instructions generated, modified and/or updated by the LLM to update and manage the todo list", default=None)

