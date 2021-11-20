# -*- coding: utf-8 -*-

"""
Fonction utilisés pour extraitre les EPV depuis le fichier cupt
"""

import re
import json
from collections import Counter
import pandas as pd

def restructurer_cupt(fichier_input):
    """
    Récupère le fichier cupt sous forme de liste de dictionnaires. On ne prend que les phrases contenant MWE.
    Pour chaque phrase on a:
    - "sent_id" : l'identifiant de la phrase
    - "text" : le texte de la phrase
    - "MWE" : un dictionnaire avec en clé l'ID de la MWE dans la phrase et en
            valeur le type et la liste de tokens de la MWE.
    """
    with open(fichier_input, encoding="utf8") as filein:
        text = filein.read()
    text = re.sub("# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD"
                  " DEPREL DEPS MISC PARSEME:MWE\n", "", text.strip())
    text = re.sub(r"# text_en =[^\n]+\n", "", text)
    text = re.sub(r"# newdoc id =[^\n]+\n", "", text)
    text = re.sub(r"# newdoc =[^\n]+\n", "", text)
    liste_sents = text.split("\n\n")

    liste_sent_sortie = []

    for sent in liste_sents:
        lignes = sent.split("\n")
        source_sent_id = re.match(r"# source_sent_id = (.+)", lignes[0])
        source_sent_id = source_sent_id.group(1)
        text_sent = re.match(r"# text = (.+)", lignes[1])
        text_sent = text_sent.group(1)

        dico_mwe = {}  # Dico interne de phrase
        for token_line in lignes[2:]:
            token_info_liste = token_line.split("\t")
            indice_token = token_info_liste[0]
            form_token = token_info_liste[1]
            lemme_token = token_info_liste[2]
            pos_token = token_info_liste[3]
            mwe_token = token_info_liste[10]

            # Traitement de colonne MWE
            col_sep = mwe_token.split(";")
            for mark_mwe in col_sep:
                if mark_mwe == "*":
                    continue
                if ":" in mark_mwe:
                    id_mwe = mark_mwe.split(":")[0]
                    type_mwe = mark_mwe.split(":")[1]
                    dico_mwe[id_mwe] = {"type": type_mwe,
                                        "tokens_list": [form_token],
                                        "lemmes_list": [lemme_token],
                                        "pos_list": [pos_token],
                                        "indice_list": [int(indice_token)],
                                        "tokens_nbre": 1}
                    if pos_token == "PRON":
                        dico_mwe[id_mwe]["pron_info"] = {lemme_token.lower():form_token.lower()}
                else:
                    dico_mwe[mark_mwe]["tokens_list"].append(form_token)
                    dico_mwe[mark_mwe]["lemmes_list"].append(lemme_token)
                    dico_mwe[mark_mwe]["pos_list"].append(pos_token)
                    dico_mwe[mark_mwe]["indice_list"].append(int(indice_token))
                    dico_mwe[mark_mwe]["tokens_nbre"] = dico_mwe[mark_mwe]["tokens_nbre"] + 1
                    if pos_token == "PRON":
                        if "pron_info" in dico_mwe[mark_mwe].keys():
                            dico_mwe[mark_mwe]["pron_info"][lemme_token.lower()]=form_token.lower()
                        else:
                            dico_mwe[id_mwe]["pron_info"] = {lemme_token.lower():form_token.lower()}
        if dico_mwe != {}:
            liste_sent_sortie.append({"sent_id": source_sent_id,
                                      "text": text_sent, "MWE": dico_mwe})

    return liste_sent_sortie

def get_one_type_mwe_list(liste_sents_sortie, type_mwe):
    """
    Args:
        liste_sents_sortie (liste de dict): chaque phrase des trois fichiers
        (sent_id, text et MWE)
        type_mwe (str): le type demandé, "VID", "LVC.full", "LVC.cause", "IRV", "MVC"

    Returns:
        - liste_one_type (liste de dict): dictionnaire de MWEs par type
          Pour chaque MWE on a:
            - 'tokens': la liste des tokens
            - 'lemmes': la liste des lemmes
            - 'ecart_max': l'écart maximal entre ses tokens soccessives
            - 'pron_etat': liste des pronoms dans MWE, stocké sous forme de dico {lemme:form}
            - 'nbre_pron': nombre de pronoms utilisés dans MWE
            - 'type' : le type de la MWE
            - 'contexte_sent' : la phrase qui contient la MWE

        - len(all_mwe) (int): le nombre total de MWEs
    """
    all_mwe = []
    liste_one_type = []
    for sent in liste_sents_sortie:
        mwes = sent["MWE"]
        for dico in mwes.values():  # dico : le dico pour chaque MWE détectée
            ecart = 0
            if dico["tokens_nbre"] > 1:
                for i in range(len(dico["indice_list"])-1):
                    ecart = max(ecart, dico["indice_list"][i+1] - dico["indice_list"][i] - 1)
            if "pron_info" in dico.keys():
                pron_etat = dico["pron_info"]   # {lemme: form}
            else:
                pron_etat = ""
            all_mwe.append({"tokens": dico["tokens_list"],
                            "lemmes": dico["lemmes_list"],
                            "indices": dico["indice_list"],
                            "nbre_tokens": dico["tokens_nbre"],
                            "ecart_max": ecart,
                            "lemmes_cnt": Counter(dico["lemmes_list"]),
                            "type": dico["type"],
                            "pron_etat": pron_etat,
                            "nbre_pron":len(pron_etat),
                            "contexte_sent": sent["text"]})

    if type_mwe == "all":
        return all_mwe, len(all_mwe)
    else:
        for dico in all_mwe:
            if dico["type"] == type_mwe:
                liste_one_type.append(dico)
        return liste_one_type, len(liste_one_type)

