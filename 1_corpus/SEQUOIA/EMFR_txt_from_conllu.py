# -*- coding: utf-8 -*-
# Jianying LIU, Anaëlle Pierredon

"""
Crée un fichier texte brut à partir du fichier conllu.
"""

import argparse


parser = argparse.ArgumentParser(description="fichier")
parser.add_argument("corpus", help="emea ou frwiki")
args = parser.parse_args()
corpus = args.corpus

with open(f"z_fichiers_intermediaires/{corpus}.conllu", "r") as f:
    liste_texte = f.readlines()
liste = []
for i in range(len(liste_texte)):
    if liste_texte[i][:9] == "# sent_id":
        sent_id = liste_texte[i].split("# sent_id = ")[1]
        sent = liste_texte[i+1].split("# text = ")[1]
        liste.append((sent_id, sent))

with open(f"z_fichiers_intermediaires/{corpus}_textbrut.txt", "w") as f:
    for sent_id, phrase in liste:
        print(sent_id+phrase, file=f)
