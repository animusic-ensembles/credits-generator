from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from models import *


def load_font(path: Optional[str], size: int) -> ImageFont.FreeTypeFont:
    """
    Load a TTF/OTF font. Otherwise fallback to PIL's default
    """
    try:
        if path:
            return ImageFont.truetype(path, size=size)
    except OSError:
        pass

    return ImageFont.load_default()


def make_font_pack(
        title_font_path: Optional[str],
        subtitle_font_path: Optional[str],
        body_font_path: Optional[str],
        title_size: int,
        subtitle_size: int,
        body_size: int
) -> FontPack:
    return FontPack(
        title=load_font(title_font_path, title_size),
        subtitle=load_font(subtitle_font_path, subtitle_size),
        body=load_font(body_font_path, body_size)
    )


def render_card(
        plan: CardLayoutPlan,
        metrics: Metrics,
        fonts: FontPack
) -> Image.Image:
    """
    Render a CardLayoutPlan to an image
    """
    img = Image.new("RGBA", (plan.card_w, plan.card_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.fontmode = 'L'
    color = (255, 255, 255, 255)

    _draw_title_block(draw, plan, fonts, color)
    if plan.card_type == 'credits':
        _draw_credits(draw, plan, metrics, fonts, color)
    elif plan.card_type == 'list':
        _draw_list(draw, plan, metrics, fonts, color)
    elif plan.card_type == 'title_only':
        pass
    else:
        raise ValueError(f'Unknown card_type: {plan.card_type!r}')
    
    return img


def _draw_title_block(
        draw: ImageDraw.ImageDraw,
        plan: CardLayoutPlan,
        fonts: FontPack,
        color: Tuple[int, int, int, int]
) -> None:
    """
    Draw the title and optional subtitle centered horizontally
    """
    centre_x = plan.card_w // 2

    draw.text(
        (centre_x, plan.title_y),
        plan.title,
        font=fonts.title,
        fill=color,
        anchor='ma'
    )

    if plan.subtitle and plan.subtitle_y is not None:
        draw.text(
            (centre_x, plan.subtitle_y),
            plan.subtitle,
            font=fonts.subtitle,
            fill=color,
            anchor='ma'
        )


def _draw_list(
        draw: ImageDraw.ImageDraw,
        plan: CardLayoutPlan,
        metrics: Metrics,
        fonts: FontPack,
        color: Tuple[int, int, int, int]
) -> None:
    """
    Draw list in a single text column
    """


def _draw_credits(
        draw: ImageDraw.ImageDraw,
        plan: CardLayoutPlan,
        metrics: Metrics,
        fonts: FontPack,
        color: Tuple[int, int, int, int]
) -> None:
    """
    Draw credits in role/name subcolumns
    """
    body_font = fonts.body

    for col in plan.columns:
        role_x = col.x
        name_x = col.x + metrics.role_col_w + metrics.role_name_gap
        y = col.y

        role_w = max(1, metrics.role_col_w)
        name_w = max(1, col.width - metrics.role_col_w - metrics.role_name_gap)

        for block in col.blocks:
            for line in block:
                if line.role_text:
                    role_text = 