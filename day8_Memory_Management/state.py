from typing_extensions import TypedDict


class MemoryState(TypedDict):
    user_id:str
    user_input:str
    operation_result:dict