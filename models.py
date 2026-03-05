from dataclasses import dataclass
from typing import List, Dict, Optional, Literal


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

    roles: List[RoleCredit]

    list_items: List[str]

    subtitle: Optional[str] = None


@dataclass(slots=True)
class Metrics:
    """
    Formatting variables.
    """
    # Card dimensions (px)
    card_w: int
    card_h: int

    # Margins (px)
    margin_l: int
    margin_r: int
    margin_t: int
    margin_b: int

    # Title/subtitle region
    title_line_h: int
    subtitle_line_h: int
    title_gap_after: int

    # Body typography
    line_h: int

    # Columns
    max_cols: int

    col_centers: Dict[int, List[float]]
    col_width_frac: Dict[int, float]  

    # Credits layout
    role_col_w: int
    role_name_gap: int
