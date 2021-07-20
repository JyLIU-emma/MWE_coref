# -*- coding: utf-8 -*-
# Jianying Liu et Anaëlle Pierredon

"""
Ce script sert à extraire les vrai exemples
"""

import json
import csv
import re
import copy
import os
import sys
from collections import Counter
# import spacy

# Créer le répertoire
rep = f"{sys.path[0]}/ancor"
rep_result = f"{sys.path[0]}/../3_resultats"
if not os.path.exists(rep):
    os.makedirs(rep)

# Fichier d'entrée
files_dico = {"ESLO_ANCOR":"ancor_ESLO_ANCOR_080721_validation.json",
         "ESLO_CO2":"ancor_ESLO_CO2_080721_validation.json",
         "OTG":"ancor_OTG_080721_validation.json",
         "UBS":"ancor_UBS_080721_validation.json"}

def extract_exemple_from_jsonfile(files):
    new_liste = []

    # TODO
    # nlp = spacy.load('fr_core_news_sm')

    i_new_indice = 0  # id des vrais exemples
    for corpus, filename in files.items():
        # Lire le fichier
        with open(f"{rep_result}/{filename}", "r", encoding="utf8") as filein:
            texte_json = filein.read()
        dico = json.loads(texte_json)

        # extraire les exemples
        eslo_new_liste = []
        eslo_old_format = {}
        eslo_new_repetition = []
        eslo_old_repetition = {}
        for cle, valeur in dico.items():
            mwes_eslo = []
            repe_eslo = []

            for i in valeur["MWES"]:
                valid = i["VALIDATION"]

                #TODO ici
                # expre_lemme = []
                # expre = eval(i["TOKENS"])
                # doc = nlp(" ".join(expre))
                # for token in doc:
                #     expre_lemme.append(token.lemma_)
                # i["expre_lemma"] = expre_lemme
                

                i_new = copy.copy(i)
                i_new["TYPE"] = cle
                if valid == "vrai":
                    mwes_eslo.append(i)
                    i_new_indice += 1
                    i_new['indice'] = i_new_indice
                    # i_new['expr_cnt'] = Counter(i['expre_lemma'])
                    i_new['expr_cnt'] = Counter(i['LEMME'])
                    i_new['sous_corpus'] = corpus
                    eslo_new_liste.append(i_new)
                    new_liste.append(i_new)
                elif valid == "répétitions":
                    repe_eslo.append(i)
                    eslo_new_repetition.append(i_new)
                    
            eslo_old_format[cle] = {"TYPE": cle, "Nombre_COREF": len(mwes_eslo),
                                    "MWES": mwes_eslo}
            eslo_old_repetition[cle] = {"TYPE": cle, "Nombre_COREF": len(repe_eslo),
                                    "MWES": repe_eslo}
        # Écrire dans les fichiers de sortie
        
        # with open(f"{rep}/ancor_{corpus}.json", "w", encoding="utf8") as out1:
        #     json.dump(eslo_old_format, out1, indent=4, ensure_ascii=False, sort_keys=False)
        with open(f"{rep}/ancor_{corpus}_new_format.json", "w", encoding="utf8") as out2:
            json.dump(eslo_new_liste, out2, indent=4, ensure_ascii=False, sort_keys=False)

        # with open(f"{rep}/ancor_{corpus}_repe.json", "w", encoding="utf8") as out1:
        #     json.dump(eslo_old_repetition, out1, indent=4, ensure_ascii=False, sort_keys=False)
        # with open(f"{rep}/ancor_{corpus}_new_format_repe.json", "w", encoding="utf8") as out2:
        #     json.dump(eslo_new_repetition, out2, indent=4, ensure_ascii=False, sort_keys=False)
    return new_liste



def get_mwe_diff(new_liste):
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
                dico_mwe[mwe]['contextes'].append((i['TOKENS'], i['PHRASE']))
                if i['sous_corpus'] not in dico_mwe[mwe]['sous_corpus']:
                    dico_mwe[mwe]['sous_corpus'].append(i['sous_corpus'])
                break
        if not flag_trouve:
            expr_cle = " ".join(i['LEMME'])
            dico_mwe[expr_cle] = {'expr_cnt':i['expr_cnt'], 'type':i['TYPE'], 'sous_corpus':[i['sous_corpus']], 'contextes':[(i['TOKENS'], i['PHRASE'], i['FICHIER'])], 'indice':[i['indice']], 'nbre_occurrence':1}      

    with open(f"{rep}/ancor_croisement_valid.json", "w", encoding="utf8") as out3:
        json.dump(dico_mwe, out3, indent=4, ensure_ascii=False, sort_keys=False)
    return dico_mwe

def transform_to_csv(dico_mwe):
    with open(f"{rep}/compositionnalite_valid_vide.csv", "w", newline="", encoding="utf8") as csvfile:
        fieldnames = ["sous_corpus", "expression", "Phrase(s)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for mwe, mwe_content in dico_mwe.items():
            sous_corpus = ",".join(mwe_content['sous_corpus'])
            phrases = "§ " + "  § ".join([f"{contexte[0]} : {contexte[1]}" for i, contexte in enumerate(mwe_content['contextes']) if i <= 2])
            writer.writerow({"sous_corpus":sous_corpus, "expression":mwe, "Phrase(s)":phrases})

def main():
    new_liste = extract_exemple_from_jsonfile(files_dico)
    dico_mwe = get_mwe_diff(new_liste)

    # with open(f"{rep}/ancor_croisement_valid.json", "r", encoding="utf8") as fic:
    #     dico_mwe = json.load(fic)
    transform_to_csv(dico_mwe)
    

if __name__ == "__main__":
    main()


