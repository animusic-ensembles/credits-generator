import csv
import os, glob
from card import Card, parse
from credit_image import generate

cards = []
card_data = []
smaller_font_override = [] # e.g. A Cruel Angel's Thesis

with open('csv/S25 EOT Credits.csv', encoding='utf-8') as file:
    data = list(csv.reader(file))[3:]

for line in data:
    if not ''.join(line):
        cards.append(Card(card_data))
        card_data = []
        continue

    card_data.append(parse(line))
cards.append(Card(card_data))
try:
    root = os.path.dirname(os.path.abspath(__file__))
    files = glob.glob(os.path.join(root, 'Cards', '*'))

    for file in files:
        if os.path.isfile(file):
            os.remove(file)
    print('All old cards deleted successfully.')
except OSError:
    print('Error occurred while deleting old cards.')

with open('csv/setlist.csv', 'w', encoding='utf-8') as out:
    for i in range(len(cards)):
        image = generate(cards[i], cards[i].title in smaller_font_override)
        image.save(f'Cards/{i:02d}.png', 'PNG', transparent=0)
        if cards[i].subtitle:
            out.write(f'{cards[i].title},{cards[i].subtitle}\n')

print('All cards generated successfully.')
