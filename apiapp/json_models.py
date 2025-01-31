from enum import Enum

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class PriorityLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class Message(BaseModel):
    priority: PriorityLevel
    title: Annotated[str, Field(min_length=1)]
    message: str = ""
    