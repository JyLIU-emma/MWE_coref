# -*- coding: utf-8 -*-
# Anaëlle Pierredon et Jianying Liu

"""
Ce script sert à récupérer les résultats des annotations manuelles en degré de compositionnalité du dossier
4_compositionnalite/ et les ajouter aux fichiers *_validation du répertoire 3_resultats/
Les fichiers non annotés en degré de compositionnalité doivent être placés dans 3_resultats/z_anciens/
"""

import json
import pandas as pd
import glob as glb


def ajouter_annotations(file, dico_mwe_degre):
    """
    Ajoute les annotations en degré de compositionnalité aux expressions correspondantes
    Returns:
        validation (dict), le dictionnaire avec les annotations complétées
    """
    with open(file, 'r') as filein:
        validation = json.load(filein)
    for mwe_type in validation:
        for mwe in validation[mwe_type]["MWES"]:
            lemmes = ' '.join(mwe['LEMMES'])
            if lemmes in dico_mwe_degre:
                mwe['DEGRE DE COMPOSITIONNALITE'] = dico_mwe_degre[lemmes]
    return validation


def main():
    """
    Ajouter les annotations en degré de compositionnalité
    """

    # Récupérer les valeurs des annotations
    degre_df = pd.read_csv("test_compositionnalite_resultats.csv")
    dico_mwe_degre = {}
    for ind in degre_df.index:
        dico_mwe_degre[degre_df['forme canonique'][ind]] = degre_df['Degré'][ind]

    # Trouver les expressions et ajouter les annotations
    for file in glb.glob("../3_resultats/z_anciens/*_validation.json"):
        new_file = ''.join(file.split('/z_anciens'))
        validation = ajouter_annotations(file, dico_mwe_degre)

        # Créer les nouveaux fichiers annotés
        with open(new_file, 'w') as fileout:
            json.dump(validation, fileout, indent=4, ensure_ascii=False,
                      sort_keys=False)


if __name__ == "__main__":
    main()
