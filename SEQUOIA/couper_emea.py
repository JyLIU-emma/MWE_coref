# -*- coding: utf-8 -*-
# Anaëlle Pierredon

import argparse

def trouver_lignes(fichier, sent_id):
    phrase_complete = []
    phrase_en_cours = False
    with open(fichier, 'r') as filein:
        for line in filein:
            if line.startswith("# source_sent_id") and sent_id == line.split()[-1]:
                phrase_en_cours = True
            if phrase_en_cours:
                if line.startswith("# source_sent_id") and sent_id != line.split()[-1]:
                    phrase_en_cours = False
                else:
                    phrase_complete.append(line.rstrip())
    return phrase_complete


def main():
    parser = argparse.ArgumentParser(description="fichier")
    parser.add_argument("new_file", help="fichier en sortie (sans extension)")
    parser.add_argument("num", help="Nombre de phrases")
    args = parser.parse_args()

    cupt_new = f"{args.new_file}.cupt"
    txt_new = f"{args.new_file}.txt"
    cupt_melange = "sequoia-ud.cupt"
    endfile = int(args.num)

    zeros = "00000"
    phrases = []
    for cnt in range(1, endfile + 1):
        sent_id = f"emea-fr-dev_{zeros[len(str(cnt)):5]}{cnt}"
        phrases.append(trouver_lignes(cupt_melange, sent_id))

    with open(cupt_new, 'w') as fileout:
        for phrase in phrases:
            for line in phrase:
                fileout.write(line)
                fileout.write('\n')
    with open(txt_new, 'w') as fileout:
        for phrase in phrases:
            for line in phrase:
                if line.startswith('# text = '):
                    line = line.split(' = ')
                    fileout.write(line[1])
                    fileout.write('\n')
    
if __name__ == "__main__":
    main()
