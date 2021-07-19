# -*- coding: utf-8 -*-
# Jianying Liu et Anaëlle Pierredon

"""
Ce script sert à extraire les vrai exemples
"""

import json
import re
import copy
import os
import sys
import spacy

nlp = spacy.load('fr_core_news_sm')

# Fichier d'entrée
filename = "ancor_ESLO_ANCOR_080721_validation.json"
# Créer le répertoire
rep = f"{sys.path[0]}/test"
if not os.path.exists(rep):
    os.makedirs(rep)
# Lire le fichier
with open(filename, "r", encoding="utf8") as filein:
    texte_json = filein.read()
dico = json.loads(texte_json)

# Diviser en sous-corpus
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
        expre_lemme = []
        expre = eval(i["TOKENS"])
        doc = nlp(" ".join(expre))
        for token in doc:
            expre_lemme.append(token.lemma_)
        i["expre_lemma"] = expre_lemme
        

        i_new = copy.copy(i)
        i_new["TYPE"] = cle
        if valid == "vrai":
            mwes_eslo.append(i)
            eslo_new_liste.append(i_new)
        elif valid == "répétitions":
            repe_eslo.append(i)
            eslo_new_repetition.append(i_new)
            
    eslo_old_format[cle] = {"TYPE": cle, "Nombre_COREF": len(mwes_eslo),
                            "MWES": mwes_eslo}
    eslo_old_repetition[cle] = {"TYPE": cle, "Nombre_COREF": len(repe_eslo),
                            "MWES": repe_eslo}

# souscorpus = {"ESLO_CO2": (eslo_old_format, eslo_new_liste),
#               "long": (long_old_format, long_new_liste),
#               "tele": (tele_old_format, tele_new_liste),
#               "short": (short_old_format, short_new_liste)}

# Écrire dans les fichiers de sortie
# for name, data in souscorpus.items():
with open(f"{rep}/ancor_ESLO_ANCOR.json", "w", encoding="utf8") as out1:
    json.dump(eslo_old_format, out1, indent=4, ensure_ascii=False, sort_keys=False)
with open(f"{rep}/ancor_ESLO_ANCOR_new_format.json", "w", encoding="utf8") as out2:
    json.dump(eslo_new_liste, out2, indent=4, ensure_ascii=False, sort_keys=False)
with open(f"{rep}/ancor_ESLO_ANCOR_repe.json", "w", encoding="utf8") as out1:
    json.dump(eslo_old_repetition, out1, indent=4, ensure_ascii=False, sort_keys=False)
with open(f"{rep}/ancor_ESLO_ANCOR_new_format_repe.json", "w", encoding="utf8") as out2:
    json.dump(eslo_new_repetition, out2, indent=4, ensure_ascii=False, sort_keys=False)
