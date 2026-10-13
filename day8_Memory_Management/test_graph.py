from graph import app


user_id="day8_graph_test"
test_inputs=[
    "我正在准备 AI Agent 实习",
    "我主要使用 Java 开发",
    "我现在主要使用 Python 开发",
    "请忘记我的主要编程语言偏好",
    "帮我计算一下 1 + 1"

]
for user_input in test_inputs:
    print("\n用户输入：",user_input)
    result=app.invoke({
        "user_id":user_id,
        "user_input":user_input,
        "operation_result":{}
    })
    print("LangGraph实际返回值：", result)
    operation_result=result["operation_result"]
    print("操作类型：",operation_result["action"])
    print("操作说明：",operation_result["message"])
    print("当前记忆：",operation_result["current_memory"])