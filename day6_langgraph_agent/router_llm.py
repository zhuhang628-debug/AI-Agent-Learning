from llm import llm
def llm_router(state):
    prompt=f"""
    你是一个意图分类助手。
    根据用户输入判断任务类型
    只能返回下面面三个类别之一：
    weather
    attraction
    travel
    
    用户输入:
    {state["user_input"]}
    
    只能返回类别名称。
    """
    response=llm.invoke(prompt)
    intent=response.content.strip()
    print("llm判断意图",intent)
    state["intent"]=intent
    return state
