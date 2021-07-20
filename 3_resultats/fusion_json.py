"""
Script sert à fusionner les fichiers sorties json, en ajoutant les nouveaux infos de lemma dans les fichiers déjà manuellement annoter.
"""

# exemple de lancement:
# python fusion_json.py ER_0-100_080721.json ER_0-100_080721_validation.json

import json
import argparse

parser = argparse.ArgumentParser(description="intégrer l'info de lemma de nouvelle sortie json dans le fichier validation")
parser.add_argument("blind", help="fichier json sans annotation de validation")
parser.add_argument("valid", help="fichier json avec annotation humaine de validation")
args = parser.parse_args()

with open(args.valid, "r", encoding="utf8") as old:
    dico_mwe = json.load(old)

with open(args.blind, "r", encoding="utf8") as new:
    dico_mwe_lemme = json.load(new)

mwes = []
for cle, valeur in dico_mwe_lemme.items():
    counter = 0
    for i in valeur["MWES"]:
        fichier = i["FICHIER"]
        phrase = i["PHRASE"]
        tokens = i["TOKENS"]
        lemme = i["LEMME"]
        mwes.append({"fichier":fichier, "phrase":phrase, "tokens":tokens, "lemme":lemme})
        counter += 1


for cle, valeur in dico_mwe.items():
    for i in valeur["MWES"]:
        fichier = i["FICHIER"]
        phrase = i["PHRASE"]
        tokens = i["TOKENS"]
        for mwe in mwes:
            if fichier == mwe['fichier'] and phrase == mwe['phrase'] and tokens == mwe['tokens']:
                i["LEMME"] = mwe['lemme']
                break

with open(args.valid, "w", encoding="utf8") as out:
    json.dump(dico_mwe, out, indent=4, ensure_ascii=False, sort_keys=False)
        


