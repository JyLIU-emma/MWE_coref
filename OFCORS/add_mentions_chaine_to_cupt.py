# -*- coding: utf-8 -*-
# Jianying Liu, Anaëlle Pierredon

"""
usage :
python add_mentions_chaine_to_cupt.py chemin/vers/mentions_output.json chemin/vers/cupt chemin/vers/resulting_chains.json chemin/vers/fichier_sortie
exemple:
python add_mentions_chaine_to_cupt.py ofcors_outputs/mentions_detection/mentions_output.json blabla_config48.cupt ofcors_outputs/resulting_chains.json fichier.cuptmc
"""

import json
import sys
import re


def lecture_mentions(mentions):
    """
    Lecture du fichier mentions, restructurer les données.
    Args:
        mentions : string
    Returns:
        mentions: liste contient l'id de mention, les tokens de mentions et
        l'info de span, exemple:
        [("1",["Pierre"],[0]), ("2",["sa","Soeur"],[2,3])]
    """
    with open(mentions) as file:
        text = file.read()
    dico_mentions = json.loads(text)

    mentions = []
    for cle, ment in dico_mentions.items():
        span = [i for i in range(ment["START"], ment["END"]+1)]
        mentions.append((cle, ment["CONTENT"], span))
    return mentions


def ajout_mentions(liste_lignes, mentions):
    """
    forme de sortie:
    {
        indice_ligne: {"indice_token_dans_texte":0, contenu_ligne_cupt:"", "mentions":["1","2"...mention_id]}
        0 : {"token_i":0, "content":"bla bla", "mentions"}
        }
    """
    new = {}
    numero_ligne = 0
    token_i = -1

    token_repete = []  # liste pour stocker les id comme 2-4

    # ajouter l'indice de tokens
    for ligne in liste_lignes:
        if ligne[0] != "#" and ligne != "\n":
            # traitement pour cas: au--à le, du--de le, des--de les ...;
            # le numéro global de chaque token, n'incrémente pas pour le cas répété
            no_token_sent = ligne.split("\t")[0]
            if no_token_sent in token_repete:
                token_repete.remove(no_token_sent)
            else:
                token_i += 1

            new[numero_ligne] = {"token_i": token_i, "content": ligne.strip()}

            # stocker les 2 lignes suivantes répétés
            match_index = re.match(r"^([0-9]+)-([0-9]+)$", no_token_sent)
            if match_index:
                token_repete = [match_index.group(1), match_index.group(2)]
        else:
            # pour ligne de commentaire: numéro de token: -1
            new[numero_ligne] = {"token_i": -1, "content": ligne.strip()}
        new[numero_ligne]["mentions"] = []
        numero_ligne += 1

    # ajouter l'info sur mentions détectées
    for ment_i, _, ment_span in mentions:
        for i in ment_span:
            for cle in range(numero_ligne):
                if new[cle]["token_i"] == i:
                    new[cle]["mentions"].append(ment_i)
    return new


def lecture_chaine_coref(resulting_chain, file=True):
    """
    Peut prendre un dico ou un fichier dans l'entrée, restructurer l'info
    Args:
        fichier chaine: resulting_chain.json
        file: booleen pour montrer si l'entrée est un file ou un dico (file par défault)
    Returns:
        dico_mention_cluster : quand on trouve les chaînes: dico sous forme: {id_mention:no_cluster}  {"1":"0", "2":"0"}
        None : rien est trouvé
    """
    if file:
        with open(resulting_chain) as filein:
            text = filein.read()
        dico_json = json.loads(text)
    else:
        dico_json = resulting_chain

    if dico_json["clusters"] != {}:
        clusters = dico_json.get("clusters")
        dico_mention_cluster = {}
        for no_cluster, mentions in clusters.items():
            for id_mention in mentions:
                dico_mention_cluster[id_mention] = no_cluster
        return dico_mention_cluster
    return None


def ajout_chaine(lignes_new, dico_chaine):
    """
    Ajoute la colonne de chaine de coréférence.
    """
    for indice_ligne in range(len(lignes_new)):
        liste_mentions = lignes_new[indice_ligne]["mentions"]
        lignes_new[indice_ligne]["chaine_coref"] = []
        if dico_chaine and liste_mentions != []:
            for ment in liste_mentions:
                if ment in dico_chaine:
                    no_chaine = dico_chaine[ment]
                    lignes_new[indice_ligne]["chaine_coref"].append(f"{no_chaine}:{ment}")
    return lignes_new


def ecrit_dans_fichier(sortie, new):
    """
    Écrit le fichier de sortie.
    """
    nombre_ligne = len(new)
    with open(sortie, "w") as fileout:
        for i in range(nombre_ligne):
            if new[i]["token_i"] != -1:
                if new[i]["mentions"] == []:
                    print(new[i]["content"]+"\t*\t*", file=fileout)
                else:
                    if new[i]["chaine_coref"] == []:
                        new_ligne = f'{new[i]["content"]}\t' + \
                                    f'{";".join(new[i]["mentions"])}\t*'
                    else:
                        new_ligne = f'{new[i]["content"]}\t' + \
                                    f'{";".join(new[i]["mentions"])}\t' + \
                                    f'{";".join(new[i]["chaine_coref"])}'
                    print(new_ligne, file=fileout)
            else:
                if i == 0:
                    new[i]["content"] = new[i]["content"] + " MENTION COREF"
                print(new[i]["content"], file=fileout)


if __name__ == "__main__":
    # -------------------------------------------------------
    # obtenir les donnees qu'on a besoin, reformuler
    fichier_mention = sys.argv[1]
    liste_mention_endroit = lecture_mentions(fichier_mention)

    fichier_cupt = sys.argv[2]
    with open(fichier_cupt) as f:
        lignes_cupt = f.readlines()

    fichier_chaine = sys.argv[3]
    dico_coref = lecture_chaine_coref(fichier_chaine)   # can be none

    # -------------------------------------------------------
    # fusionner les infos
    lignes_avec_mentions = ajout_mentions(lignes_cupt, liste_mention_endroit)
    lignes_mention_coref = ajout_chaine(lignes_avec_mentions, dico_coref)

    # for cle,valeur in lignes_mention_coref.items():
    #     print(cle, valeur)
    # 16 {'token_i': 9, 'content': '1\tIl\til\tPRON\t_\tGender=Masc|Number=Sing|Person=3|PronType=Prs\t2\tnsubj\t_\t_\t*', 'mentions': ['5', '6'], 'chaine_coref': ['4:5', '4:6']}
    # 17 {'token_i': 10, 'content': '2\tvit\tvivre\tVERB\t_\tMood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin\t0\troot\t_\t_\t*', 'mentions': ['5', '6'], 'chaine_coref': ['4:5', '4:6']}
    # 18 {'token_i': 11, 'content': '3\tà\tà\tADP\t_\t_\t4\tcase\t_\t_\t*', 'mentions': ['6', '7'], 'chaine_coref': ['4:6']}

    # -------------------------------------------------------
    # formatter la ligne et ecrire dans le fichier
    fichier_sortie = sys.argv[4]
    ecrit_dans_fichier(fichier_sortie, lignes_mention_coref)
