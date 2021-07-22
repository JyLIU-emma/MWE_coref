# -*- coding: utf-8 -*-
# Jianying Liu et Anaëlle Pierredon

import json
import csv
import os
import sys
import glob
import random
from collections import Counter

def transform_to_csv(dico_mwe, corpus_name, rep):
    """
    Générer le fichier csv pour google doc
    """
    cles = list(dico_mwe.keys())
    random.shuffle(cles)
    with open(f"{rep}/{corpus_name}_compositionnalite_vide.csv", "w", newline="", encoding="utf8") as csvfile:
        fieldnames = ["sous_corpus", "expression", "Phrase(s)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",",
                                quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for mwe in cles:
            sous_corpus = dico_mwe[mwe].get('sous_corpus', "Sequoia")
            if sous_corpus != "Sequoia":
                sous_corpus = ", ".join(sous_corpus)
            phrases = "§ " + "  § ".join([f"{contexte[0]} : {contexte[1]}" for i, contexte in enumerate(dico_mwe[mwe]['contextes']) if i <= 2])
            writer.writerow({"sous_corpus": sous_corpus,
                             "expression": mwe,
                             "Phrase(s)": phrases})

def choisir_samples(categories, nombre, liste_mwe):
    new_liste = []
    for i, mwe in liste_mwe.items():
        if mwe["type"] in categories:
            new_liste.append(i)
    samples = random.sample(new_liste, nombre)
    mwe_samples = {}
    for cle in samples:
        mwe_samples[cle] = liste_mwe[cle]
    return mwe_samples

def main():
    rep_parent = sys.path[0]
    nombre = int(sys.argv[1])
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
    
    # trier tous les faux cas, l'ecrire dans un json
    mwe_fauxcas = sorted(dico_mwe_fauxcas.items(), key=lambda x:x[1]["nbre_occurrence"], reverse=True)
    with open(f"{rep_parent}/fauxcas_mwe.json", "w", encoding="utf8") as out:
        json.dump(mwe_fauxcas, out, indent=4, ensure_ascii=False,
                sort_keys=False)
    
    categories = ["VID", "LVC.cause", "LVC.full"]
    samples = choisir_samples(categories, nombre, dico_mwe_fauxcas)
    with open(f"{rep_parent}/fauxcas_mwe_samples{nombre}.json", "w", encoding="utf8") as out:
        json.dump(samples, out, indent=4, ensure_ascii=False,
            sort_keys=False)

    dico_mwe_vrai.update(samples)
    transform_to_csv(dico_mwe_vrai, "melange", rep_parent)

if __name__ == "__main__":
    main()




