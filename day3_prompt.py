from langchain_core.prompts import ChatPromptTemplate

prompt=ChatPromptTemplate.from_template(
    """
你是一名AI Agent开发导师

请回答用户的问题:

{question}
"""
)

message=prompt.invoke(
    {
        "question":"什么是LangGraph？"
    }
)
print(message)