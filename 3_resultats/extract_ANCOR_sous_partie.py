# -*- coding: utf-8 -*-
# Jianying Liu et Anaëlle Pierredon
"""
Script sert à séparer le fichier sorti de corpus ANCOR à des sous-corpus:
ESLO_CO2 : contient CO2_ESLO_001_C, CO2_ESLO_002_C et CO2_ESLO_003_C
long : contient des dialogues longs, noms du fichier sous format [0-9]{3}_C.*
tele : contient les dialogues téléphoniques, noms du fichier sous format [0-9]{3}_[0-9a-z]+
short : contient des dialogues courts, exemple de nom du fichier: 1AG0531
"""
import json
import re
import copy
import os
import sys

# fichier d'entrée
filename = "ancor_020721_semivalid.json"
# créer le répertoire
rep = f"{sys.path[0]}/{filename[:12]}"
if not os.path.exists(rep):
    os.makedirs(rep)
# lire le fichier
with open(filename, "r", encoding="utf8") as filein:
    texte_json = filein.read()
dico = json.loads(texte_json)

# diviser en sous-corpus
eslo_new_liste = []
eslo_old_format = {}
long_new_liste = []
long_old_format = {}
tele_new_liste = []
tele_old_format = {}
short_new_liste = []
short_old_format = {}
for cle, valeur in dico.items():
    mwes_eslo = []
    mwes_long = []
    mwes_tele = []
    mwes_short = []
    for i in valeur["MWES"]:
        i_new = copy.copy(i)
        i_new["TYPE"] = cle
        fichier = i["FICHIER"]
        if fichier[:8] == "CO2_ESLO":
            mwes_eslo.append(i)
            eslo_new_liste.append(i_new)
        elif re.match(r"[0-9][A-Z]{2}[0-9]{4}_mwe", fichier):
            mwes_short.append(i)
            short_new_liste.append(i_new)
        elif re.match(r"[0-9]{3}_[0-9]+", fichier):
            mwes_tele.append(i)
            tele_new_liste.append(i_new)
        else:
            mwes_long.append(i)
            long_new_liste.append(i_new)
    eslo_old_format[cle]= {"TYPE":cle, "Nombre_COREF":len(mwes_eslo), "MWE":mwes_eslo}
    long_old_format[cle]= {"TYPE":cle, "Nombre_COREF":len(mwes_long), "MWE":mwes_long}
    tele_old_format[cle]= {"TYPE":cle, "Nombre_COREF":len(mwes_tele), "MWE":mwes_tele}
    short_old_format[cle]= {"TYPE":cle, "Nombre_COREF":len(mwes_short), "MWE":mwes_short}
            
souscorpus = {"ESLO_CO2":(eslo_old_format,eslo_new_liste), 
              "long":(long_old_format, long_new_liste), 
              "tele":(tele_old_format, tele_new_liste), 
              "short":(short_old_format, short_new_liste)}

# écrire dans les fichiers sortis
for name,data in souscorpus.items():
    with open(f"{rep}/{name}_old_format.json", "w", encoding="utf8") as out1:
        json.dump(data[0], out1, indent=4, ensure_ascii=False, sort_keys=False)
    with open(f"{rep}/{name}_new_format.json", "w", encoding="utf8") as out2:
        json.dump(data[1], out2, indent=4, ensure_ascii=False, sort_keys=False)