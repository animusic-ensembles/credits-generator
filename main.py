import os, glob
from parser import parse_cards_csv
from layout import layout_card_with_fallback
from renderer import render_card, save_card

filename = 'csv/F25 EOT Credits.csv'

try:
    root = os.path.dirname(os.path.abspath(__file__))
    files = glob.glob(os.path.join(root, 'Cards', '*'))

    for file in files:
        if os.path.isfile(file):
            os.remove(file)
    print('All old cards deleted successfully.')
except OSError:
    print('Error occurred while deleting old cards.')

cards = parse_cards_csv(filename)

for card in cards:
    plan = layout_card_with_fallback(card)
    img = render_card(plan)
    save_card(img, f'Cards/{card.card_id}.png')