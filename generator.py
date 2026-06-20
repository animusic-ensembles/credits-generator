from __future__ import annotations

import io
import tempfile
import zipfile
from pathlib import Path

from layout import layout_card_with_fallback
from parser import ParseError, parse_cards_csv
from renderer import render_card


def build_archive(contents: bytes) -> io.BytesIO:
    """Parse CSV bytes and return a ZIP containing the rendered PNG cards."""
    with tempfile.TemporaryDirectory() as temp_dir:
        csv_path = Path(temp_dir) / 'upload.csv'
        csv_path.write_bytes(contents)
        cards = parse_cards_csv(csv_path)

    if not cards:
        raise ParseError('No credit cards were found', 1, [])

    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as output:
        for card in cards:
            plan = layout_card_with_fallback(card)
            image = render_card(plan)
            image_data = io.BytesIO()
            image.save(image_data, format='PNG')
            output.writestr(f'{card.card_id}.png', image_data.getvalue())
    archive.seek(0)
    return archive
