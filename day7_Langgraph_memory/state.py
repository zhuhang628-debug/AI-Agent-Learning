from typing import TypedDict
from typing import Annotated

from langgraph.graph import add_messages


class MemoryState(TypedDict):
    messages:Annotated[list,add_messages]
    user_id:str