from pathlib import Path

from parser import parse_cards_csv
from layout import layout_card_with_fallback
from renderer import render_card, save_card

ROOT = Path(__file__).resolve().parent
DEFAULT_CSV = ROOT / 'csv' / 'W26 EOT Credits.csv'
DEFAULT_OUTPUT = ROOT / 'Cards'


def generate_cards(csv_path: str | Path, output_dir: str | Path) -> list[Path]:
    """Parse a CSV and write its rendered credit cards to output_dir."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cards = parse_cards_csv(csv_path)
    paths: list[Path] = []

    for card in cards:
        plan = layout_card_with_fallback(card)
        image = render_card(plan)
        path = output_dir / f'{card.card_id}.png'
        save_card(image, path)
        paths.append(path)

    return paths


if __name__ == '__main__':
    for old_card in DEFAULT_OUTPUT.glob('*'):
        if old_card.is_file():
            old_card.unlink()
    generate_cards(DEFAULT_CSV, DEFAULT_OUTPUT)
