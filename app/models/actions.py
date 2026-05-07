from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    TYPE = "type"
    PRESS_ENTER = "press_enter"
    PRESS_PF = "press_pf"
    NAVIGATE_MENU = "navigate_menu"
    WAIT = "wait"


class Action(BaseModel):
    action: ActionType
    value: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Plan(BaseModel):
    reasoning: str = ""
    actions: list[Action] = Field(default_factory=list)
