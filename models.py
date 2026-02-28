from dataclasses import dataclass
from typing import List, Optional, Literal


@dataclass(slots=True)
class RoleCredit:
    """
    Represents a single role in the credits (e.g. Violin, Trumpet, Conductor)
    and the names associated with it.
    """
    role: str    
    names: List[str]


CardType = Literal['credits', 'list', 'title_only']


@dataclass(slots=True)
class CardData:
    """
    The credit card to render.
    """
    card_id: str
    title: str
    card_type: CardType

    header_roles: List[RoleCredit]
    performer_roles: List[RoleCredit]

    list_items: List[str]

    subtitle: Optional[str] = None


