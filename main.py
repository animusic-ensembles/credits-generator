import csv
import os, glob
from card import Card, parse
from credit_image import generate

cards = []
card_data = []

with open('F24 Anicafe Credits.csv', encoding='utf-8') as file:
    data = list(csv.reader(file))[3:]

for line in data:
    if ''.join(line) == '':
        cards.append(Card(card_data))
        card_data = []
        continue

    card_data.append(parse(line))

try:
    files = glob.glob(os.path.join('/Cards', '*'))
    for file in files:
        if os.path.isfile(file):
            os.remove(file)
    print('All old cards deleted successfully.')
except OSError:
    print('Error occurred while deleting old cards.')

for i in range(len(cards)):
    image = generate(cards[i])
    image.save(f'Cards/{i:03d}.png')

print('All cards generated successfully.')
