# -*- coding: utf-8 -*-
# Anaëlle Pierredon

"""
Créer un dictionnaire de la totalité des MWEs dans Sequoia
(train, dev et test).
"""


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
    phrase = phrase.split('\n')
    for line in phrase:
        if line.startswith("#") or line.strip() == "":
            continue
        line = line.strip().split('\t')
        mwes = line[10]
        if mwes != "*":
            for mwe in mwes.split(';'):
                infos = mwe.split(':')
                id_mwe = int(infos[0])-1
                if len(infos) == 2:
                    liste_mwes[id_mwe] = [line[1]]
                    liste_types.append(infos[1])
                else:
                    liste_mwes[id_mwe].append(line[1])

    dico_mwes = {}
    for indice, tokens in liste_mwes.items():
        type_mwe = liste_types[indice]
        if type_mwe in dico_mwes:
            dico_mwes[type_mwe].append(tokens)
        else:
            dico_mwes[type_mwe] = []
            dico_mwes[type_mwe].append(tokens)
    return dico_mwes


def dico_complet(dico_mwe_phrase, dico_mwe_all):
    """
    Entrées : dico_mwe_phrase, le dictionnaire des MWE d'une seule phrase
              dico_mwe_all, le dictionnaire de toutes les MWEs de sequoia

    Sortie : dico_mwe_all, le dictionnaire de toutes les MWEs de sequoia
    """
    for cle, valeur in dico_mwe_phrase.items():
        if cle in dico_mwe_all:
            dico_mwe_all[cle].extend(valeur)
        else:
            dico_mwe_all[cle] = []
            dico_mwe_all[cle].extend(valeur)
    return dico_mwe_all


def affichage_stats(dico_mwe_all):
    """
    Afficher les statistiques du dictionnaire
    """
    total = 0
    for cle, valeur in dico_mwe_all.items():
        print(f"{cle} : {len(valeur)}")
        total += len(valeur)
    print(f"total MWE : {total}")


def affichage_dico(dico_mwe_all):
    """
    Afficher le dictionnaire
    """
    for cle, valeur in dico_mwe_all.items():
        print(f"{cle} : {valeur}")


if __name__ == "__main__":
    fichiers = ["fr_sequoia-ud-test.cupt", "fr_sequoia-ud-dev.cupt",
                "fr_sequoia-ud-train.cupt"]
    dico_mwe_all = {}

    liste_phrase = []
    for fichier in fichiers:
        sortie = lecture(fichier)
        liste_phrase.extend(sortie)

    for phrase in liste_phrase:
        dico_mwe_phrase = dico_phrase(phrase)
        dico_mwe_all = dico_complet(dico_mwe_phrase, dico_mwe_all)

    affichage_stats(dico_mwe_all)
    # affichage_dico(dico_mwe_all)
