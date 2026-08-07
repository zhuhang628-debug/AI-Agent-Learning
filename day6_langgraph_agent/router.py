def route_question(state):
    intent=state["intent"]
    if intent=="weather":
        return "weather"
    elif intent=="attraction":
        return "attraction"
    elif intent=="travel":
        return "travel"
    else:
        return "answer"