# -*- coding: utf-8 -*-
# Anaëlle Pierredon et Jianying Liu

"""
Créer les 4 fichiers de sortie de OFCORS à partir des annotations du corpus
ANCOR en utilisant le module AncorParsing de OFCORS pour chaque fichier du
répertoire donné en argument
Les fichiers produits sont :
- <fichier>.txt: Le texte brut
- ofcors_outputs/<fichier>_tokens.json: Le texte tokenisé
- ofcors_outputs/<fichier>_mentions_output.json: chaque mention
                                            (content, start, end, start-end)
- ofcors_outputs/<fichier>_resulting_chains.json : chaque chaîne de mentions
"""

import re
import os
import json
import argparse
import glob
from ofcors import ancorparsing as ap


class AncorToken():
    """
    Token du corpus ANCOR

    Attributs:
        text (str): le token
        ancor_id (str): son identifiant dans le fichier TEI (s1.u2.w7)
        unite (int): Le numéro de l'unité indiqué par ancor_id (2)
        id (int): L'identifiant global du token (l'id du premier mot du
                  fichier est à 0 et s'incrémente jusqu'au dernier)
    """
    def __init__(self, text, ancor_id, unite, out_id):
        self.text = text
        self.ancor_id = ancor_id
        self.unite = unite
        self.id = out_id


def find_tokens(file, namefile, path):
    """
    Récupère les tokens du fichier TEI et créer les fichiers
    ofcors_outputs/{fichier}.txt et ofcors_outputs/{fichier}_tokens.json et
    crée une liste des tokens du fichier.

    Args:
        file (str), le fichier TEI du corpus ANCOR
        namefile (str), le nom du fichier sans l'extension
        path (str), le chemin vers le dossier qui contient les fichiers TEI
    Returns:
        ancor_tokens (liste de AncorToken), la liste des tokens du fichier
    """
    raw_text = ""
    tokens_file = {}
    ancor_tokens = []
    cnt = 0
    encours = 0

    for unite in file.root.iter('{http://www.tei-c.org/ns/1.0}u'):
        for word in unite.iter():
            if word.tag == "{http://www.tei-c.org/ns/1.0}w" or word.tag == "{http://www.tei-c.org/ns/1.0}pc":
                ancor_id = "#" + word.attrib["{http://www.w3.org/XML/1998/namespace}id"]
                unite = int(re.search(r'u([0-9]+)', ancor_id).group(1))
                word = AncorToken(word.text, ancor_id, unite, cnt)
                ancor_tokens.append(word)
                if word.unite != encours:
                    raw_text += "\n\n"
                    encours = word.unite
                raw_text += f"{word.text} "
                tokens_file[cnt] = word.text
                cnt += 1

    chemin = f"{path}{namefile}.txt"
    with open(chemin, 'w') as textfile:
        print(chemin)
        textfile.write(raw_text)

    chemin = f"{path}ofcors_outputs/{namefile}_tokens.json"
    with open(chemin, 'w') as textfile:
        print(chemin)
        json.dump(tokens_file, textfile)

    return ancor_tokens


def find_mentions(file, namefile, path, ancor_tokens):
    """
    Récupère les mentions du fichier TEI et créer le fichier
    ofcors_outputs/{fichier}_mentions_output.json

    Args:
        file (str), le fichier TEI du corpus ANCOR
        namefile (str), le nom du fichier sans l'extension
        path (str), le chemin vers le dossier qui contient les fichiers TEI
        ancor_tokens (liste de AncorToken), la liste des tokens du fichier
    Returns:
        mentions (dict), les infos sur les mentions du fichier TEI
    """
    mentions_ancor = file.get_mentions()

    cnt = 0
    mentions = {}
    for mention_id, dico_ment in mentions_ancor.items():
        mentions[cnt] = {}
        mentions[cnt]['CONTENT'] = get_mention_content(ancor_tokens,
                                                       dico_ment['START_ID'],
                                                       dico_ment['END_ID'])
        mentions[cnt]['MENTION_ID'] = mention_id
        mentions[cnt]['START'] = get_token_id(ancor_tokens,
                                              dico_ment['START_ID'])
        mentions[cnt]['END'] = get_token_id(ancor_tokens, dico_ment['END_ID'])
        mentions[cnt]['SPAN-ID'] = f"{mentions[cnt]['START']}-{mentions[cnt]['END']}"
        cnt += 1

    chemin = f"{path}ofcors_outputs/{namefile}_mentions_output.json"
    with open(chemin, 'w') as textfile:
        print(chemin)
        json.dump(mentions, textfile)

    return mentions


def find_chains(file, namefile, path, mentions):
    """
    Trouve les chaînes de coréférence du fichier TEI et créer le fichier
    ofcors_outputs/{fichier}_resulting_chains.json

    Args:
        file (str), le fichier TEI du corpus ANCOR
        namefile (str), le nom du fichier sans l'extension
        path (str), le chemin vers le dossier qui contient les fichiers TEI
        mentions (dict), les infos sur les mentions du fichier TEI

    """
    coref_ancor = file.get_coreferences()
    coref_ancor = file.compute_chains(coref_ancor)

    clusters = {}
    for cnt, chaine in coref_ancor.items():
        clusters[cnt] = []
        for ment in chaine:
            ment = get_mention_id(mentions, ment)
            clusters[cnt].append(ment)

    coref = {"type": "clusters", "clusters": clusters}

    chemin = f"{path}ofcors_outputs/{namefile}_resulting_chains.json"
    with open(chemin, 'w') as textfile:
        print(chemin)
        json.dump(coref, textfile)


def get_token_id(ancor_tokens, ancor_id):
    """
    Récupère l'ID global correspondant à l'ID d'ANCOR.

    Args:
        ancor_tokens (liste de AncorToken), la liste des tokens du fichier TEI
        ancor_id (str), l'identifiant de token d'ANCOR
    Returns:
        (str), l'identifiant global correspondant
    """
    for token in ancor_tokens:
        if token.ancor_id == ancor_id:
            res = str(token.id)
    return res


def get_mention_content(ancor_tokens, start, end):
    """
    Récupère la liste des tokens correspondant à la mention.

    Args:
        ancor_tokens (liste de AncorToken), la liste des tokens du fichier TEI
        start (str), l'ID ANCOR du début de la mention
        end (str), l'ID ANCOR de la fin de la mention
    Returns:
        res (liste de str), la liste des tokens de la mention
    """
    res = []
    for cnt, token in enumerate(ancor_tokens):
        if token.ancor_id == start:
            res.append(token.text)
            if start == end:
                return res
            start = ancor_tokens[cnt+1].ancor_id
    return res


def get_mention_id(mentions, ancor_id):
    """
    Récupère l'identifiant de mention correspondant à l'identifiant d'ANCOR

     Args:
        mentions (dict), les infos sur les mentions du fichier TEI
        ancor_id (str), l'identifiant de mention d'ANCOR
    Returns:
        res (str), l'ID de la mention
    """
    for identifiant, mention in mentions.items():
        if mention['MENTION_ID'] == ancor_id:
            res = str(identifiant)
    return res


def main():
    """
    Créer les fichiers de sortie d'OFCORS à partir des annotations d'ANCOR
    """
    parser = argparse.ArgumentParser(description="fichier")
    parser.add_argument("rep", help="répertoire contenant les fichiers .tei")
    args = parser.parse_args()

    if not os.path.exists(f"{args.rep}/ofcors_outputs"):
        os.makedirs(f"{args.rep}/ofcors_outputs")
    path = args.rep

    # Pour chaque fichier du répertoire
    for file in glob.glob(f"{path}*.tei"):

        namefile = file.split('/')[-1].split('.')[0]
        file = ap.XMLTEIFileReader(file)

        # FICHIER.TXT et FICHIER_TOKEN.JSON
        ancor_tokens = find_tokens(file, namefile, path)

        # FICHIER_MENTIONS_OUTPUT.JSON
        mentions = find_mentions(file, namefile, path, ancor_tokens)

        # FICHIER_RESULTING_CHAINS.JSON
        find_chains(file, namefile, path, mentions)


if __name__ == "__main__":
    main()
