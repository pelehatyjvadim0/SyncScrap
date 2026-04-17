from root.apps.workers.scout.logic.strategies.avito import AvitoScoutStrategy
from root.apps.workers.scout.logic.strategies.base import BaseScoutStrategy
from root.apps.workers.scout.logic.strategies.default import DefaultScoutStrategy
from root.apps.workers.scout.logic.strategies.registry import (
    ScoutStrategyRegistry,
    default_scout_strategy_registry,
)

__all__ = [
    "AvitoScoutStrategy",
    "BaseScoutStrategy",
    "DefaultScoutStrategy",
    "ScoutStrategyRegistry",
    "default_scout_strategy_registry",
]
