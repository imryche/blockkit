from enum import Enum

__all__ = ["ListStyle", "Style", "TriggerActionsOn", "Include"]


class ListStyle(str, Enum):
    ordered = "ordered"
    bullet = "bullet"


class Style(str, Enum):
    primary = "primary"
    danger = "danger"


class TriggerActionsOn(str, Enum):
    on_enter_pressed = "on_enter_pressed"
    on_character_entered = "on_character_entered"


class Include(str, Enum):
    im = "im"
    mpim = "mpim"
    private = "private"
    public = "public"
