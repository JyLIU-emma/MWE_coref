# -*- coding: utf-8 -*-
# Jianying Liu et Anaëlle Pierredon

"""
Pour lancer ce script, il faut avoir le fichier  z_fichiers_intermediaires/ER_info.json
Ensuite:
python3 get_ER_texte.py
"""

import re
import json
import os
import sys

rep = sys.path[0]

def parsing_cupt(fichier_input, souscorpus):
    """
    Extraire le sous-corpus demandé depuis le fichier cupt de sequoia.
    Args:
        fichier_input(str) : chemin vers le fichier global à extraire
        souscorpus(str) : nom de sous-corpus utilisé dans le source_sent_id,
            soit "annodis.er", "frwiki_50.1000", "emea-fr-test" ou "emea-fr-dev", "Europar.550"
    Returns:
        liste_sent_sortie(list) : une liste des dictionnaires de phrase, contenant l'info sur
            le source_sent_id, texte brut de la phrase, id chiffré initial de la phrase,
            l'int du id de phrase moins 1 et le block de cette phrase dans le fichier cupt
    """
    with open(fichier_input) as f:
        text = f.read()
    text = re.sub("# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC PARSEME:MWE\n","",text.strip())
    liste_sents = text.split("\n\n")

    liste_sent_sortie = []

    for sent in liste_sents:
        lignes = sent.split("\n")
        source_sent_id = re.match(r"# source_sent_id = (.+)",lignes[0])
        source_sent_id = source_sent_id.group(1)
        matcher = re.search(souscorpus, source_sent_id)
        if matcher:
            num_sent = source_sent_id.split(f"{souscorpus}_")[-1]
            text_sent = re.match(r"# text = (.+)",lignes[1])
            text_sent = text_sent.group(1)
            liste_sent_sortie.append({"sent_id":source_sent_id, "text":text_sent, "id":num_sent, "numero_sent": int(num_sent)-1, "cupt":sent})
    return liste_sent_sortie

def get_article_begin(liste_sent):
    """
    Trouver l'indice des phrases frontières
    Args:
        liste_sent(list): liste globale des phrases, sortie fusionnée et ordonnée de la fonction parsing_cupt
    Returns:
        l'indice de phrase débute chaque article
    """
    with open(f"{rep}/z_fichiers_intermediaires/ER_info.json","r", encoding="utf8") as fic:
        info = json.loads(fic.read())

    compteur = 0
    no_trouve = []
    liste_debut = []
    for item in info:
        titre = item["titre"]
        flag = False
        for sent in liste_sent:
            texte_sent = sent["text"]   
            if titre == texte_sent:
                compteur += 1
                flag = True
                # print(sent["numero_sent"], titre)
                liste_debut.append(sent["numero_sent"])
                break
        if not flag:
            no_trouve.append(item)
    liste_debut.sort()

    print(f"Nombre articles trouves : {compteur}")
    print(f"no trouve: {len(no_trouve)}")
    for i in no_trouve:
        print(i)
    return liste_debut


def create_corpus_folder(liste_debut, new_l, path):
    """
    Organiser le résultat et les écrire dans répertoire
    Args:
        liste_debut(list): l'indice de première phrase de chaque article
        new_l(list) : liste globale des phrases, sortie fusionnée et ordonnée de la fonction parsing_cupt
        path(str) : chemin du répertoire de corpus à créer
    """
    # creation du répertoire de corpus
    if not os.path.exists(path):
        os.makedirs(path)

    article_i = 1
    # pour chaque article
    for i, numero_sent in enumerate(liste_debut):
        article_cupt = []
        article_txt = []
        debut = numero_sent
        if i < len(liste_debut) - 1:
            fin = liste_debut[i+1] - 1
        else:
            fin = new_l[-1]["numero_sent"]
        # pour chaque phrase
        while debut <= fin:
            article_cupt.append(new_l[debut]["cupt"])
            article_txt.append(new_l[debut]["text"])
            debut += 1
        cupt = "# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC PARSEME:MWE\n" + "\n\n".join(article_cupt)
        txt = "\n".join(article_txt)
        with open(f"{path}/annodisER_{article_i}.cupt", "w", encoding="utf8") as cuptfile:
            cuptfile.write(cupt)
        with open(f"{path}/annodisER_{article_i}.txt", "w", encoding="utf8") as txtfile:
            txtfile.write(txt)
        
        article_txt = []
        article_cupt = []
        article_i += 1



def main():
    # corpus folder path
    path = rep + "/annodisER"

    # obtenir la liste globale des phrases (3 fichiers) ordonnees
    liste_sent = []
    for cate in ["test", "dev", "train"]:
        fic = f"{rep}/z_corpus_initial/fr_sequoia-ud-{cate}.cupt"
        liste_sent.extend(parsing_cupt(fic, "annodis.er"))
    new_l = sorted(liste_sent, key=lambda x:x["numero_sent"])

    # Stocker phrases extraites dans un fichier json
    with open(rep + "/annodisER.json","w") as f:
        f.write(json.dumps(new_l, indent=4))

    liste_debut = get_article_begin(new_l)
    create_corpus_folder(liste_debut, new_l, path)

if __name__ == "__main__":
    main()


    


