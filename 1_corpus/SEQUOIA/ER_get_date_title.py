# -*- coding: utf-8 -*-
# Jianying Liu et Anaëlle Pierredon

"""
Script sert à générer le fichier ER_info_a_corriger.json, qui contient les
dates et titres potentiels des articles utilisés dans PARSEME/Sequoia
après, il faut vérifier et corriger manuellement les titres incohérents
Le fichier stocker dans z_fichiers_intermediaires est déjà corrigé

Pour lancer ce script:
Télécharger le corpus depuis: http://redac.univ-tlse2.fr/corpus/annodis/ANNODIS_rr.zip
Dézipper le corpus et placer ce script dans son répertoire racine
Ensuite:
    python3 ER_get_date_title.py
"""

import glob
import re
import json

rep = "./annotations_expert/texte/A/"  # ANNODIS_rr

liste = glob.glob(rep+'news*.seg')
print(len(liste))

info = []
for filepath in liste:
    date = filepath.split("_")[-1][:-4]
    date = date.split("-")
    jour, mois, an = date[0], date[1], date[2]
    # print(jour, mois, an)
    date = "-".join([an, mois, jour])
    # dates.append(date)
    with open(filepath, "r", encoding="utf8") as fic:
        texte = fic.read()
    match = re.search(r"\[(.+?)\]_1", texte)
    titre = match.group(1)
    item = {"date": date, "titre": titre}
    info.append(item)

with open("ER_info_a_corriger.json", "w", encoding="utf8") as sortie:
    sortie.write(json.dumps(info, indent=4))
# print(info)
