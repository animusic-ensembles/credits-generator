from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import List, Optional, Sequence

from models import *
import config

@dataclass(slots=True)
class LayoutDoesNotFitError(Exception):
    card_id: str
    total_lines: int
    max_col: int

    def __str__(self) -> str:
        return f'LayoutDoesNotFitError(Card {self.card_id}): {self.total_lines} lines does not fit into {self.max_col} column(s).'


def layout_card(card: CardData, metrics: Metrics) -> CardLayoutPlan:
    """
    Generate a layout plan for a card
    """
    content_left = metrics.margin_l
    content_right = metrics.card_w - metrics.margin_r
    content_top = metrics.margin_t
    content_bottom = metrics.card_h - metrics.margin_b

    usable_h = max(0, content_bottom - content_top)
    title_block_h = _get_title_block_height(card.subtitle, metrics)

    if card.card_type == 'title_only':
        stack_h = title_block_h
        stack_top = content_top + (usable_h - stack_h) // 2
        title_y = stack_top
        subtitle_y = (title_y + metrics.title_line_h if card.subtitle else None)
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
            subtitle_y=subtitle_y,
            body_y=stack_top + stack_h,
            body_bottom=stack_top + stack_h,
            columns=[],
            list_items=[]
        )
    
    max_body_h = max(0, usable_h - title_block_h - metrics.title_gap_after)

    if card.card_type == 'list':
        packed = _layout_list(card.card_id, card.list_items, metrics, max_body_h)
        body_lines = _get_max_column_lines(packed)
        body_h = body_lines * metrics.line_h

        stack_h = title_block_h + metrics.title_gap_after + body_h
        stack_top = content_top + (usable_h - stack_h) // 2
        title_y = stack_top
        subtitle_y = (title_y + metrics.title_line_h if card.subtitle else None)
        body_y = stack_top + title_block_h + metrics.title_gap_after
        body_bottom = body_y + body_h

        cols = _materialize_columns(packed, len(packed), metrics, content_left, content_right, body_y)
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
        packed = _layout_credits(card.card_id, card.roles, metrics, max_body_h)
        body_lines = _get_max_column_lines(packed)
        body_h = body_lines * metrics.line_h

        stack_h = title_block_h + metrics.title_gap_after + body_h
        stack_top = content_top + (usable_h - stack_h) // 2
        title_y = stack_top
        subtitle_y = (title_y + metrics.title_line_h if card.subtitle else None)
        body_y = stack_top + title_block_h + metrics.title_gap_after
        body_bottom = body_y + body_h
        
        cols = _materialize_columns(packed, len(packed), metrics, content_left, content_right, body_y)
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


def _get_title_block_height(subtitle: Optional[str], metrics: Metrics) -> int:
    """
    Height of the title/subtitle stack, excluding the gap before the body
    """
    height = metrics.title_line_h
    if subtitle:
        height += metrics.subtitle_line_h
    return height


def _get_max_column_lines(packed: List[List[List[CreditLine]]]) -> int:
    """
    Tallest column height, in text lines
    """
    if not packed:
        return 0
    return max(sum(len(block) for block in col) for col in packed)


def _layout_list(
        card_id: str,
        items: Sequence[str],
        metrics: Metrics,
        max_body_h: int
) -> List[List[List[CreditLine]]]:
    """
    Layout for a single column of credits
    """
    lines_per_col = max(1, max_body_h // metrics.line_h)
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

            return packed
    
    raise LayoutDoesNotFitError(card_id, total_lines, metrics.max_cols)


def _layout_credits(
        card_id: str,
        roles: Sequence[RoleCredit],
        metrics: Metrics,
        max_body_h: int
) -> List[List[List[CreditLine]]]:
    """
    Layout for credit cards
    """
    lines_per_col = max(1, max_body_h // metrics.line_h)
    total_lines = sum(len(role.names) for role in roles)

    for k in range(1, max(1, metrics.max_cols) + 1):
        if total_lines <= k * lines_per_col:
            return _fill_columns(roles, k, lines_per_col)
    
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

            block_lines: List[CreditLine] = []
            for i, name in enumerate(chunk):
                role_text = role.role if i == 0 else ''
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