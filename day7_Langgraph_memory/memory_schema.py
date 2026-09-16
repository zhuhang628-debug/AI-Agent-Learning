from pydantic import BaseModel


class UserMemory(BaseModel):
    language:str | None=None
    goal:str | None=None
    interest:str | None=None