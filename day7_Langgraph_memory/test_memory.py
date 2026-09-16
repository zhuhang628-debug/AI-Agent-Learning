from langchain_core.messages import HumanMessage

from graph import app

#用户1
config_zhuhang={
    "configurable":{
        "thread_id":"zhuhang"
    }
}

# result1 = app.invoke(
#     {
#         "messages": [
#             HumanMessage(content="我是朱航")
#         ]
#     },
#     config=config_zhuhang
# )
#
# print("===== 第一次 =====")
# print(result1["messages"][-1].content)


result2 = app.invoke(
    {
        "messages": [
            HumanMessage(content="我叫什么")
        ]
    },
    config=config_zhuhang
)

print("===== 第二次 =====")
print(result2["messages"][-1].content)