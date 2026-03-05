from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import List, Optional, Sequence

from models import CardData, RoleCredit, Metrics
import config

@dataclass(slots=True)
class LayoutDoesNotFitError(Exception):
    card_id: str
    total_lines: int
    max_col: int

    def __str__(self) -> str:
        return f'LayoutDoesNotFitError(Card {self.card_id}): {self.total_lines} lines does not fit into {self.max_col} column(s).'


# A single credit line
# Entirely semantic
@dataclass(slots=True)
class CreditLine:
    role_text: str
    name_text: str


# Layout for a single column of credits
@dataclass(slots=True)
class ColumnLayout:
    x: int
    y: int
    width: int
    blocks: List[List[CreditLine]]
    total_lines: int


# Complete layout plan for a card
@dataclass(slots=True)
class CardLayoutPlan:
    card_id: str
    card_type: str
    title: str
    subtitle: Optional[str]

    card_w: int
    card_h: int
    content_left: int
    content_right: int
    content_top: int
    content_bottom: int

    title_y: int
    body_y: int
    body_bottom: int

    columns: List[ColumnLayout]
    list_items: List[str]


def layout_card(card: CardData, metrics: Metrics) -> CardLayoutPlan:
    """
    Generate a layout plan for a card
    """
    content_left = metrics.margin_l
    content_right = metrics.card_w - metrics.margin_r
    content_top = metrics.margin_t
    content_bottom = metrics.card_h - metrics.margin_b

    title_y = content_top
    y = title_y + metrics.title_line_h
    if card.subtitle:
        y += metrics.subtitle_line_h
    y += metrics.title_gap_after

    body_y = y
    body_bottom = content_bottom

    if card.card_type == 'title_only':
        return CardLayoutPlan(
            card_id=card.card_id,
            card_type=card.card_type,
            title=card.title,
            subtitle=card.subtitle,
            card_w=metrics.card_w,
            card_h=metrics.card_h,
            content_left=content_left,
            content_right=content_right,
            content_top=content_top,
            content_bottom=content_bottom,
            title_y=title_y,
            body_y=body_y,
            body_bottom=body_bottom,
            columns=[],
            list_items=[]
        )
    if card.card_type == 'list':
        cols = _layout_list(card.card_id, card.list_items, metrics, content_left, content_right, body_y, body_bottom)
        return CardLayoutPlan(
            card_id=card.card_id,
            card_type=card.card_type,
            title=card.title,
            subtitle=card.subtitle,
            card_w=metrics.card_w,
            card_h=metrics.card_h,
            content_left=content_left,
            content_right=content_right,
            content_top=content_top,
            content_bottom=content_bottom,
            title_y=title_y,
            body_y=body_y,
            body_bottom=body_bottom,
            columns=cols,
            list_items=card.list_items
        )
    if card.card_type == 'credits':
        cols = _layout_credits(card.card_id, card.roles, metrics, content_left, content_right, body_y, body_bottom)
        return CardLayoutPlan(
            card_id=card.card_id,
            card_type=card.card_type,
            title=card.title,
            subtitle=card.subtitle,
            card_w=metrics.card_w,
            card_h=metrics.card_h,
            content_left=content_left,
            content_right=content_right,
            content_top=content_top,
            content_bottom=content_bottom,
            title_y=title_y,
            body_y=body_y,
            body_bottom=body_bottom,
            columns=cols,
            list_items=[]
        )
    
    raise ValueError(f'Unknown card_type: {card.card_type!r}')


def layout_card_with_fallback(card: CardData):
    """
    Try normal theme, and if it doesn't fit within max_col, try again with a smaller theme.
    """
    try:
        return layout_card(card, config.METRICS)
    except LayoutDoesNotFitError:
        return layout_card(card, config.METRICS_SMALL)


def _layout_list(
        card_id: str,
        items: Sequence[str],
        metrics: Metrics,
        content_left: int,
        content_right: int,
        body_y: int,
        body_bottom: int
) -> List[ColumnLayout]:
    """
    Layout for a single column of credits
    """
    available_h = max(0, body_bottom - body_y)
    lines_per_col = max(1, available_h // metrics.line_h)
    total_lines = len(items)

    for k in range(1, max(1, metrics.max_cols) + 1):
        if total_lines <= k * lines_per_col:
            packed: List[List[List[CreditLine]]] = [[] for _ in range(k)]

            idx = 0
            total_remaining = total_lines
            for col in range(k):
                if total_remaining <= 0:
                    break
                remaining_cols = k - col
                target = ceil(total_remaining / remaining_cols)
                take = min(lines_per_col, target)
                chunk = items[idx: idx + take]
                idx += take
                total_remaining -= take

                packed[col] = [[CreditLine(role_text='', name_text=name) for name in chunk]]

            return _materialize_columns(packed, k, metrics, content_left, content_right, body_y)
    
    raise LayoutDoesNotFitError(card_id, total_lines, metrics.max_cols)


def _layout_credits(
        card_id: str,
        roles: Sequence[RoleCredit],
        metrics: Metrics,
        content_left: int,
        content_right: int,
        body_y: int,
        body_bottom: int
) -> List[ColumnLayout]:
    """
    Layout for credit cards
    """
    available_h = max(0, body_bottom - body_y)
    lines_per_col = max(1, available_h // metrics.line_h)

    total_lines = sum(len(r.names) for r in roles)

    for k in range(1, max(1, metrics.max_cols) + 1):
        if total_lines <= k * lines_per_col:
            packed = _fill_columns(roles, k, lines_per_col)
            return _materialize_columns(packed, k, metrics, content_left, content_right, body_y)
    
    raise LayoutDoesNotFitError(card_id, total_lines, metrics.max_cols)


def _fill_columns(
        roles: Sequence[RoleCredit],
        k: int,
        lines_per_col: int
) -> List[List[List[CreditLine]]]:
    """
    Fill columns with credit blocks while preserving role order
    Columns are filled left-to-right
    """
    total_remaining = sum(len(r.names) for r in roles)
    role_idx = 0
    name_idx = 0

    cols: List[List[List[CreditLine]]] = [[] for _ in range(k)]
    
    for col in range(k):
        if total_remaining <= 0:
            break

        remaining_cols = k - col
        target = ceil(total_remaining / remaining_cols)
        limit = min(lines_per_col, target)
        lines_left = limit

        while total_remaining > 0 and lines_left > 0:
            role = roles[role_idx]
            names = role.names

            if name_idx >= len(names):
                role_idx += 1
                name_idx = 0
                continue

            take = min(len(names) - name_idx, lines_left)
            chunk = names[name_idx : name_idx + take]

            show_role = (name_idx == 0)
            block_lines: List[CreditLine] = []
            for i, name in enumerate(chunk):
                role_text = role.role if (show_role and i == 0) else ''
                block_lines.append(CreditLine(role_text=role_text, name_text=name))
            
            cols[col].append(block_lines)

            name_idx += take
            total_remaining -= take
            lines_left -= take

            if name_idx >= len(names):
                role_idx += 1
                name_idx = 0
    
    return cols


def _materialize_columns(
        packed_lines: List[List[List[CreditLine]]],
        k: int,
        metrics: Metrics,
        content_left: int,
        content_right: int,
        body_y: int
) -> List[ColumnLayout]:
    """
    Convert packed credit lines into positioned columns
    """
    content_w = content_right - content_left
    
    centres = metrics.col_centers.get(k) or metrics.col_centers[max(metrics.col_centers)]
    width_frac = metrics.col_width_frac.get(k) or metrics.col_width_frac[max(metrics.col_width_frac)]
    col_w = int(content_w * width_frac)

    cols: List[ColumnLayout] = []
    for i in range(k):
        cx = content_left + int(content_w * centres[i])
        x = cx - col_w // 2

        blocks = packed_lines[i] if i < len(packed_lines) else []
        total_lines = sum(len(b) for b in blocks)

        cols.append(ColumnLayout(x=x, y=body_y, width=col_w, blocks=blocks, total_lines=total_lines))

    for c in cols:
        if c.x < content_left or (c.x + c.width) > content_right:
            raise ValueError("Column geometry exceeds content bounds. ")
    
    return cols