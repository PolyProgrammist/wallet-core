import os
import json

for file in os.listdir('twtassets'):
    file = 'twtassets/' + file + '/info.json'
    a = {}
    with open(file) as f:
        a = json.load(f)
    a['decimals'] = int(a['decimals'])
    explstr = 'https://tonscan.org/jetton/'
    a['explorer'] = 'https://tonscan.org/address/' + a['explorer'][len(explstr):]

    with open(file, 'w') as f:
        json.dump(a, f, indent=4)