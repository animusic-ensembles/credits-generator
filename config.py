from __future__ import annotations

from dataclasses import replace
from PIL import ImageFont
from typing import Optional
from models import Metrics, FontPack


def _load_font(path: Optional[str], size: int) -> ImageFont.FreeTypeFont:
    try:
        if path:
            return ImageFont.truetype(path, size=size)
    except OSError:
        pass
    return ImageFont.load_default()


def _line_height(font: ImageFont.FreeTypeFont) -> int:
    ascent, descent = font.getmetrics()
    total_height = ascent + abs(descent)
    return int(total_height)


FONT_PATH = 'font/NotoSansJP-Regular.ttf'
LIGHT_FONT_PATH = 'font/NotoSansJP-Light.ttf'

TITLE_FONT_SIZE = 40
SUBTITLE_FONT_SIZE = 36
BODY_FONT_SIZE = 32
SMALL_FONT_SIZE = 28

FONTS = FontPack(
    title=_load_font(FONT_PATH, TITLE_FONT_SIZE),
    subtitle=_load_font(LIGHT_FONT_PATH, SUBTITLE_FONT_SIZE),
    roles=_load_font(LIGHT_FONT_PATH, BODY_FONT_SIZE),
    names=_load_font(FONT_PATH, BODY_FONT_SIZE)
)

FONTS_SMALL = FontPack(
    title=_load_font(FONT_PATH, TITLE_FONT_SIZE),
    subtitle=_load_font(LIGHT_FONT_PATH, SUBTITLE_FONT_SIZE),
    roles=_load_font(LIGHT_FONT_PATH, SMALL_FONT_SIZE),
    names=_load_font(FONT_PATH, SMALL_FONT_SIZE)
)

METRICS = Metrics(
    card_w=1920,
    card_h=1080,

    margin_l=100,
    margin_r=100,
    margin_t=100,
    margin_b=100,

    title_line_h=_line_height(FONTS.title),
    subtitle_line_h=_line_height(FONTS.subtitle),
    title_gap_after=20,

    line_h=_line_height(FONTS.names),

    max_cols=3,
    
    col_centers={
        1: [0.50],
        2: [0.33, 0.67],
        3: [0.17, 0.50, 0.83]
    },

    col_width_frac={
        1: 0.70,
        2: 0.44,
        3: 0.27,
    },

    role_col_w=260,
    role_name_gap=24
)

METRICS_SMALL = replace(METRICS, line_h=_line_height(FONTS_SMALL.names))
