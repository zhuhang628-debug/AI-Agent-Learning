class ChatHistory:
    def __init__(self):
        self.history = [
            {
                "role": "system",
                "content": "你是一名AI Agent开发导师，负责指导我学习LangChain和LangGraph"
            }
        ]

    def add_message(self,role, content):
        self.history.append({"role": role, "content": content})

    def get_history(self):
        return self.history
