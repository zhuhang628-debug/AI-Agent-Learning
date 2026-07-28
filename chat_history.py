history=[
    {
        "role":"system",
        "content":"你是一个专业的AI助手"
    }
]

def add_message(role,content):
    history.append({"role":role,"content":content})

def get_history():
    return history