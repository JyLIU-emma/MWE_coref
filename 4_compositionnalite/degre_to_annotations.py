# -*- coding: utf-8 -*-
# Anaëlle Pierredon et Jianying Liu

"""
Ce script sert à récupérer les résultats des annotations manuelles en degré de compositionnalité du dossier
4_compositionnalite/ et les ajouter aux fichiers: 
    1) 4_compositionnalite/resultats_mwes/*_croisement_mwe.json
    2) 3_resultats/*_validation.json
Et puis, basant sur les nouveaux fichiers *_validation.json , renouveler les fichiers resultats_croisements/*_mwelist.json

Les fichiers non annotés en degré de compositionnalité doivent être placés dans 3_resultats/z_anciens/
"""

import json
import pandas as pd
import glob as glb
from extract_vrai_exemple import renouvellement


def get_degre_dico(filecsv):
    """
    Récupérer les valeurs des annotations
    """
    degre_df = pd.read_csv(filecsv, encoding="utf8")
    dico_mwe_degre = {}
    for ind in degre_df.index:
        dico_mwe_degre[degre_df['Expression'][ind]] = degre_df['Degré'][ind]
    return dico_mwe_degre

def ajouter_annotations_mwe(file, dico_mwe_degre):
    """
    Ajouter les annotations en degré de compositionnalité dans les fichiers resultats_mwes/*_croisement_mwe.json
    Créer une liste des exemples avec l'annotation de degré
    Returns:
        croisement_liste (list): les mwe avec les annotations complétées
    """
    with open(file, "r", encoding="utf8") as filein:
        mwes = json.load(filein)
    
    croisement_liste = []
    for mwe in mwes.keys():
        degre_mwe = dico_mwe_degre.get(mwe,"")
        mwes[mwe]["DEGRE DE COMPOSITIONNALITE"] = degre_mwe
        for crois in mwes[mwe]["contextes"]:
            exemple = {"tokens":crois[0], "phrase":crois[1], "file":crois[2], "degre":degre_mwe}
            croisement_liste.append(exemple)

    with open(file, "w", encoding="utf8") as output:
        json.dump(mwes, output, indent=4, ensure_ascii=False,
                      sort_keys=False)
    print(f"Renouvellement du fichier '{file}' (ajout de degré de compositionnalité)")
    return croisement_liste
    

def ajouter_annotations(file, croisement_liste):
    """
    Ajoute les annotations en degré de compositionnalité aux expressions correspondantes
    Returns:
        validation (dict), le dictionnaire avec les annotations complétées
    """
    with open(file, 'r', encoding="utf8") as filein:
        validation = json.load(filein)
    for mwe_type in validation:
        for mwe in validation[mwe_type]["MWES"]:
            for exemple in croisement_liste:
                if exemple["tokens"] == mwe["TOKENS"] and exemple["file"] == mwe["FICHIER"] and exemple["phrase"] == mwe["PHRASE"] :
                    mwe['DEGRE DE COMPOSITIONNALITE'] = exemple["degre"]
                    break
    return validation


def main():
    # Récupérer les valeurs des annotations
    filecsv = "test_compositionnalite_resultats.csv"
    dico_mwe_degre = get_degre_dico(filecsv)

    # Ajouter l'annotation dans resultats_mwes/*_croisement_mwe.json et extraitre les exemples avec annotation degré
    crois_list = []
    for file in glb.glob("resultats_mwes/*_croisement_mwe.json"):
        crois_list.extend(ajouter_annotations_mwe(file,dico_mwe_degre))

    # Trouver les expressions et ajouter les annotations
    for file in glb.glob("../3_resultats/z_anciens/*_validation.json"):
        new_file = ''.join(file.split('/z_anciens'))
        validation = ajouter_annotations(file, crois_list)

        # Créer les nouveaux fichiers annotés
        with open(new_file, 'w', encoding="utf8") as fileout:
            json.dump(validation, fileout, indent=4, ensure_ascii=False,
                      sort_keys=False)
    
    # Renouveler les fichier *_mwelist.json
    renouvellement("ancor")
    renouvellement("sequoia")
    renouvellement("ER")

if __name__ == "__main__":
    main()
