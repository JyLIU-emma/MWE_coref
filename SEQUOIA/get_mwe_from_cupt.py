# -*- coding: utf-8 -*-
# Jianying LIU, Anaëlle Pierredon

"""
Réunit les fichiers "fr_sequoia-ud-dev.cupt", "fr_sequoia-ud-test.cupt" et
"fr_sequoia-ud-train.cupt" puis fait une liste des MWEs selon leur type.

Les résultats sont écrits dans les fichiers MWE_decompte_{type}.json .
Un fichier MWE_decompte.json est également créé avec l'ensemble des phrases
contenant au moins une MWE.
"""

import re
import json


def restructurer_cupt(fichier_input):
    """
    Récupère le fichier cupt sous forme de liste de dictionnaires.
    Pour chaque phrase on a:
    - "sent_id" : l'identifiant de la phrase
    - "text" : le texte de la phrase
    - "MWE" : un dictionnaire avec en clé l'ID de la MWE dans la phrase et en
            valeur le type et la liste de tokens de la MWE.
    """
    with open(fichier_input) as filein:
        text = filein.read()
    text = re.sub("# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD"
                  " DEPREL DEPS MISC PARSEME:MWE\n", "", text.strip())
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
            form_token = token_info_liste[1]
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
                                        "tokens_list": [form_token]}
                else:
                    dico_mwe[mark_mwe]["tokens_list"].append(form_token)
        if dico_mwe != {}:
            liste_sent_sortie.append({"sent_id": source_sent_id,
                                      "text": text_sent, "MWE": dico_mwe})

    return liste_sent_sortie


def get_one_type_mwe_list(liste_sents_sortie, type_mwe):
    """
    Args:
        liste_sents_sortie (liste de dict): chaque phrase des trois fichiers
        (sent_id, text et MWE)
        type_mwe (str): le type demandé

    Returns:
        - liste_one_type (liste de dict): dictionnaire de MWEs par type
          Pour chaque MWE on a:
            - 'content': la liste des tokens
            - 'type' : le type de la MWE
            - 'contexte_sent' : la phrase qui contient la MWE

        - len(all_mwe) (int): le nombre total de MWEs
    """
    all_mwe = []
    liste_one_type = []
    for sent in liste_sents_sortie:
        mwes = sent["MWE"]
        for dico in mwes.values():
            all_mwe.append({"content": dico["tokens_list"],
                            "type": dico["type"],
                            "contexte_sent": sent["text"]})

    for dico in all_mwe:
        if dico["type"] == type_mwe:
            liste_one_type.append(dico)

    return liste_one_type, len(all_mwe)


def main():
    """
    Écrit les fichiers de décompte pour chaque type et un fichier de décompte
    global.
    """
    fic_1 = "z_corpus_initial/fr_sequoia-ud-test.cupt"
    fic_2 = "z_corpus_initial/fr_sequoia-ud-dev.cupt"
    fic_3 = "z_corpus_initial/fr_sequoia-ud-train.cupt"
    liste_1 = restructurer_cupt(fic_1)
    liste_2 = restructurer_cupt(fic_2)
    liste_3 = restructurer_cupt(fic_3)
    liste_complete = liste_1 + liste_2 + liste_3

    # Voir la structure de cette liste de phrases
    with open("MWE_decompte.json", "w") as fileout:
        fileout.write(json.dumps(liste_complete, indent=4))

    types_mwe = ['VID', 'IRV', 'LVC.full', 'LVC.cause', 'MVC']
    for typ in types_mwe:
        liste_one_type, len_all = get_one_type_mwe_list(liste_complete, typ)
        print(typ, ":", len(liste_one_type))
        with open(f"MWE_decompte_{typ}.json", "w") as file:
            file.write(json.dumps(liste_one_type, indent=4))
    print("total MWE:", len_all)


if __name__ == "__main__":
    main()
