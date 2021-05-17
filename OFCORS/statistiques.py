# -*- coding: utf-8 -*-
# Anaëlle Pierredon

"""
Production de statistiques sur la totalité des MWE des différents fichiers.
Argument : répertoire où se trouvent les cupt+
"""

import glob
import argparse

def lecture(fichier):
    """
    Lecture des fichiers.
    Entrée : fichier, un nom de fichier
    sortie : filein, une liste des phrases du fichier
    """
    with open(fichier, 'r') as filein:
        filein = filein.read().split('\n\n')
    return filein


def dico_phrase(phrase):
    """
    Dictionnaire des MWE par phrases
    Entrée : phrase, la liste des lignes de la phrase
    Sortie : dico_mwe, le dictionnaire des MWE de cette phrase
    """
    liste_mwes = {}
    liste_types = []
    liste_chaines = []
    phrase = phrase.split('\n')
    for line in phrase:
        if line.startswith('# text'):
            text = line.split(' = ')[1]
        if line.startswith("#") or line.strip() == "":
            continue
        line = line.strip().split('\t')
        mwes = line[10]
        if mwes != "*":
            for mwe in mwes.split(';'):
                infos = mwe.split(':')
                id_mwe = int(infos[0])-1
                if len(infos) == 2:
                    liste_mwes[id_mwe] = {"tokens": [line[1]], "coref": [line[12]], "phrase" : text}
                    liste_types.append(infos[1])
                else:
                    liste_mwes[id_mwe]["tokens"].append(line[1])
                    liste_mwes[id_mwe]["coref"].append(line[12])

    dico_mwes = {}
    for indice, valeurs in liste_mwes.items():
        type_mwe = liste_types[indice]
        if type_mwe in dico_mwes:
            dico_mwes[type_mwe].append(valeurs)
        else:
            dico_mwes[type_mwe] = []
            dico_mwes[type_mwe].append(valeurs)
    return dico_mwes


def dico_complet(dico_mwe_phrase, dico_mwe_all):
    """
    Entrées : dico_mwe_phrase, le dictionnaire des MWE d'une seule phrase
              dico_mwe_all, le dictionnaire de toutes les MWEs du répertoire

    Sortie : dico_mwe_all, le dictionnaire de toutes les MWEs du répertoire
    """
    for cle, valeur in dico_mwe_phrase.items():
        if cle in dico_mwe_all:
            dico_mwe_all[cle].extend(valeur)
        else:
            dico_mwe_all[cle] = []
            dico_mwe_all[cle].extend(valeur)
    return dico_mwe_all


def affichage_stats_globales(dico_mwe_all):
    """
    Afficher les statistiques globales du dictionnaire
    """
    print("------------------------")
    total = 0
    for cle, valeur in dico_mwe_all.items():
        print(f"{cle} : {len(valeur)}")
        total += len(valeur)
    print(f"total MWE : {total}")


def affichage_dico(dico_mwe_all):
    """
    Afficher le dictionnaire
    """
    print("------------------------")
    for type, infos in dico_mwe_all.items():
        print(f"{type} :")
        for dico in infos:
            print(f"\t- tokens : {dico['tokens']}, coref : {dico['coref']}")

def affichage_stats_coref(dico_mwe_all):
    """
    Afficher les statistiques du dictionnaire en rapport avec la coréférence
    """
    print("------------------------")
    total = 0
    total_coref = 0
    for cle, valeur in dico_mwe_all.items():
        nb_coref = 0
        liste = []
        total += len(valeur)
        for dico in valeur:
            coref = len([el for el in dico['coref'] if el != "*"])
            if coref > 0:
                nb_coref += 1
                total_coref += 1
                liste.append(dico)
        print(f"\n{cle} : {nb_coref} - {nb_coref}/{len(valeur)} - {round(nb_coref/len(valeur), 2)}")
        for item in liste:
            print(f"- {item['tokens']}\tcoref : {item['coref']}\n\"{item['phrase']}\"")
    print(f"\ntotal coref : {total_coref} - {total_coref}/{total} - {round(total_coref/total, 2)}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="fichier")
    parser.add_argument("rep", help="répertoire des cupt+")
    args = parser.parse_args()

    # Regrouper les fichiers en une seule liste de phrases
    liste_phrase = []
    for fichier in glob.glob(f"{args.rep}*"):
        sortie = lecture(fichier)
        liste_phrase.extend(sortie)

    dico_mwe_all = {}
    for phrase in liste_phrase:
        dico_mwe_phrase = dico_phrase(phrase)
        dico_mwe_all = dico_complet(dico_mwe_phrase, dico_mwe_all)

    affichage_dico(dico_mwe_all)
    affichage_stats_globales(dico_mwe_all)
    affichage_stats_coref(dico_mwe_all)
