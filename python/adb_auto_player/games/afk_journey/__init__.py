"""AFK Journey Game Package."""

from .afk_journey_base import AFKJourneyBase
from .config import Config
from .main import AFKJourney
from .mixins import (
    AFKStagesMixin,
    ArcaneLabyrinthMixin,
    AssistMixin,
    DurasTrialsMixin,
    EventMixin,
    LegendTrialMixin,
)

__all__: list[str] = [
    "AFKJourney",
    "AFKJourneyBase",
    "AFKStagesMixin",
    "ArcaneLabyrinthMixin",
    "AssistMixin",
    "Config",
    "DurasTrialsMixin",
    "EventMixin",
    "LegendTrialMixin",
]
