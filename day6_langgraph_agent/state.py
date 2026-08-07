from typing import TypedDict


class TravelState(TypedDict):
    user_input: str
    weather:str
    attractions:list
    answer:str
    city:str
    intent:str
