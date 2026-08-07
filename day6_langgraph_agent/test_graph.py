from graph import app

state = {
    "user_input":"帮我规划杭州三日游",
    "city":"杭州",
    "intent":"",
    "weather":"",
    "attractions":[],
    "answer":""
}
result = app.invoke(
    state
)
print(result)