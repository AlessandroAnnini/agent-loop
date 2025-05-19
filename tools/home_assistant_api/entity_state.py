from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class EntityState:
    """Data class representing a Home Assistant entity state."""

    entity_id: str
    state: str
    attributes: Dict[str, Any]
