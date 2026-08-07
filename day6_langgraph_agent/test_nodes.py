from nodes import (
    weather_node,
    attraction_node,
    answer_node
)


state = {

    "user_input":"杭州3日游",

    "weather":"",

    "attractions":[],

    "answer":""

}


state = weather_node(state)

state = attraction_node(state)

state = answer_node(state)


print(state)