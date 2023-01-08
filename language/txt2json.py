# txt2json.py

import os
import sys
import json

#-------------------------------------------------------------------------------

def txt2json(filename, langs):
    with open(filename) as f:
        rows = [r.strip() for r in f.readlines()]

    d = {
        'translations': []
    }

    arr = d['translations']

    if langs == 2:
        nb_elems = int(len(rows)/2)
        for i in range(1, nb_elems):
            arr.append({'he': rows[2*i], 'en': rows[2*i+1]})
    else:
        nb_elems = int(len(rows)/3)
        for i in range(1, nb_elems):
            arr.append({'he': rows[3*i], 'en': rows[3*i+1], 'fr': rows[3*i+2]})

    root, ext = os.path.splitext(filename)
    outfile = f'{root}.json'
    with open(outfile, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=4, ensure_ascii=False)

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <filename.txt> <langs')
        print(f'lesson1.txt, langs=2, lesson2.txt, langs=3')
        exit(1)
    txt2json(sys.argv[1], int(sys.argv[2]))