from memory_service import manage_memory
from state import MemoryState

def memory_node(state:MemoryState):
    print("执行memory_node")
    user_id=state["user_id"]
    user_input=state["user_input"]
    result=manage_memory(
        user_id=user_id,
        user_input=user_input
    )
    return {
        "operation_result":result
    }