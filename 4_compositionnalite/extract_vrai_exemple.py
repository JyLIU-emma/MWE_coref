# -*- coding: utf-8 -*-
# Jianying Liu et Anaëlle Pierredon

"""
Ce script sert à extraire les vrai exemples
pour le lancement:
- première argument à choisir entre "ancor", "sequoia" et "ER";
- ajouter le 2e si lire directement depuis un fichier

exemple :
python extract_vrai_exemple.py ancor [ancor_croisement_valid.json]
"""

import json
import csv
import os
import sys
from collections import Counter

# Créer le répertoire
rep = f"{sys.path[0]}/resultats_croisements"
rep_result = f"{sys.path[0]}/../3_resultats"
if not os.path.exists(rep):
    os.makedirs(rep)


def extract_exemple_from_jsonfile(files, corpus_global_name):
    """
    extraîre les exemples valides et reformuler la structure de json
    Returns:
        new_liste (list): liste des dico de croisement valide dans tout le corpus
    """
    # liste globale des MWE de toutes les sous-parties
    new_liste = []

    i_new_indice = 0  # id des vrais exemples
    for corpus, filename in files.items():
        # Lire le fichier
        with open(f"{rep_result}/{filename}", "r", encoding="utf8") as filein:
            texte_json = filein.read()
        dico = json.loads(texte_json)

        # extraire les exemples
        mwe_new_liste = []
        for cle, valeur in dico.items():

            for i_new in valeur["MWES"]:
                valid = i_new["VALIDATION"]
                i_new["TYPE"] = cle
                if valid == "vrai":
                    i_new_indice += 1
                    i_new['indice'] = i_new_indice
                    i_new['expr_cnt'] = Counter(i_new['LEMME'])
                    i_new['sous_corpus'] = corpus
                    mwe_new_liste.append(i_new)
                    new_liste.append(i_new)
        # Écrire dans les fichiers de sortie
        with open(f"{rep}/{corpus_global_name}_{corpus}_mwelist.json", "w", encoding="utf8") as out2:
            json.dump(mwe_new_liste, out2, indent=4, ensure_ascii=False, sort_keys=False)
    return new_liste



def get_mwe_diff(new_liste, corpus_name):
    """
    Unifier différentes formes d'une MWE, générer un fichier sortie *_croisement_valid.json
    """
    dico_mwe = {}
    for i in new_liste :
        expr = i['expr_cnt']
        flag_trouve = False
        for mwe, mwe_content in dico_mwe.items():
            expr_exist = mwe_content['expr_cnt']
            if expr == expr_exist and i['TYPE'] == mwe_content['type']:
                flag_trouve = True
                dico_mwe[mwe]['indice'].append(i['indice'])
                dico_mwe[mwe]['nbre_occurrence'] += 1
                dico_mwe[mwe]['contextes'].append((i['TOKENS'], i['PHRASE'], i['FICHIER']))
                if i['sous_corpus'] not in dico_mwe[mwe]['sous_corpus']:
                    dico_mwe[mwe]['sous_corpus'].append(i['sous_corpus'])
                break
        if not flag_trouve:
            expr_cle = " ".join(i['LEMME'])
            dico_mwe[expr_cle] = {'expr_cnt':i['expr_cnt'], 'type':i['TYPE'],
                                  'sous_corpus':[i['sous_corpus']],
                                  'contextes':[(i['TOKENS'], i['PHRASE'], i['FICHIER'])],
                                  'indice':[i['indice']], 'nbre_occurrence':1}

    with open(f"{rep}/{corpus_name}_croisement_valid.json", "w", encoding="utf8") as out3:
        json.dump(dico_mwe, out3, indent=4, ensure_ascii=False, sort_keys=False)
    return dico_mwe

def transform_to_csv(dico_mwe, corpus_name):
    """
    Générer le fichier csv pour google doc
    """
    with open(f"{rep}/{corpus_name}_compositionnalite_vide.csv", "w", newline="", encoding="utf8") as csvfile:
        fieldnames = ["sous_corpus", "expression", "Phrase(s)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",",
                                quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for mwe, mwe_content in dico_mwe.items():
            sous_corpus = ",".join(mwe_content['sous_corpus'])
            phrases = "§ " + "  § ".join([f"{contexte[0]} : {contexte[1]}" for i, contexte in enumerate(mwe_content['contextes']) if i <= 2])
            writer.writerow({"sous_corpus":sous_corpus, "expression":mwe, "Phrase(s)":phrases})

def main():
    corpus_name = sys.argv[1]
    # Fichier d'entrée
    valide = True
    if corpus_name == "ancor":
        files_dico = {"ESLO_ANCOR":"ancor_ESLO_ANCOR_080721_validation.json",
                    "ESLO_CO2":"ancor_ESLO_CO2_080721_validation.json",
                    "OTG":"ancor_OTG_080721_validation.json",
                    "UBS":"ancor_UBS_080721_validation.json"}
    elif corpus_name == "sequoia":
        files_dico = {"frwiki":"sequoia_frwiki_050721_validation.json",
                      "emea":"sequoia_emea_080721_validation.json",
                      "annodisER":"sequoia_annodisER_050721_validation.json"}
    elif corpus_name == "ER":
        files_dico = {"0-100":"ER_0-100_080721_validation.json"}
    else:
        print("Corpus name invalide.")
        valide = False

    if valide:
        try:
            filename = sys.argv[2]
            with open(f"{rep}/{filename}", "r", encoding="utf8") as fic:
                dico_mwe = json.load(fic)
        except IndexError:
            new_liste = extract_exemple_from_jsonfile(files_dico, corpus_name)
            dico_mwe = get_mwe_diff(new_liste, corpus_name)

        transform_to_csv(dico_mwe, corpus_name)

if __name__ == "__main__":
    main()
