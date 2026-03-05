from dataclasses import replace
from models import Metrics

METRICS = Metrics(
    card_w=1920,
    card_h=1080,

    margin_l=100,
    margin_r=100,
    margin_t=100,
    margin_b=100,

    title_line_h=70,
    subtitle_line_h=46,
    title_gap_after=36,

    line_h=34,

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

METRICS_SMALL = replace(METRICS, line_h=30)