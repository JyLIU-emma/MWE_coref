# -*- coding: utf-8 -*-
# Jianying Liu et Anaëlle Pierredon

import json
import csv
import os
import sys
import glob
from collections import Counter

def transform_to_csv(dico_mwe, corpus_name, rep):
    """
    Générer le fichier csv pour google doc
    """
    with open(f"{rep}/{corpus_name}_compositionnalite_vide.csv", "w", newline="", encoding="utf8") as csvfile:
        fieldnames = ["sous_corpus", "expression", "Phrase(s)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",",
                                quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for mwe, mwe_content in dico_mwe.items():
            sous_corpus = "Sequoia"
            phrases = "§ " + "  § ".join([f"{contexte[0]} : {contexte[1]}" for i, contexte in enumerate(mwe_content['contextes']) if i <= 2])
            writer.writerow({"sous_corpus": sous_corpus,
                             "expression": mwe,
                             "Phrase(s)": phrases})

def main():
    rep_parent = sys.path[0]
    chemin_mwe_fic = f"{rep_parent}/../1_corpus/SEQUOIA/MWE_decompte_global.json"
    files = glob.glob(f"{rep_parent}/*_croisement_mwe.json")

    with open(chemin_mwe_fic, "r", encoding="utf8") as chemin_mwe_fic:
        dico_mwe_all = json.load(chemin_mwe_fic)

    dico_mwe_vrai = {}
    for fic in files:
        with open(fic, "r", encoding="utf8") as ficin:
            dico_mwe_onefic = json.load(ficin)
            dico_mwe_vrai.update(dico_mwe_onefic)

    dico_mwe_fauxcas = {}
    for mwe, mwe_content in dico_mwe_all.items():
        expre = mwe_content["expr_cnt"]
        existe = False
        for i in dico_mwe_vrai.values():
            expre_vrai = i["expr_cnt"]
            if expre == expre_vrai:
                existe = True
                break
        if not existe:
            dico_mwe_fauxcas[mwe] = mwe_content
    
    mwe_fauxcas = sorted(dico_mwe_fauxcas.items(), key=lambda x:x[1]["nbre_occurrence"], reverse=True)
    with open(f"{rep_parent}/fauxcas_mwe.json", "w", encoding="utf8") as out:
        json.dump(mwe_fauxcas, out, indent=4, ensure_ascii=False,
                sort_keys=False)
    
    transform_to_csv(dico_mwe_fauxcas, "fauxcas", rep_parent)

if __name__ == "__main__":
    main()




