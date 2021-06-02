# -*- coding: utf-8 -*-
# Jianying LIU, Anaëlle Pierredon

"""
Réunit les fichiers "fr_sequoia-ud-dev.cupt", "fr_sequoia-ud-test.cupt" et
"fr_sequoia-ud-train.cupt" puis les sépare en autant de fichiers qu'il y a
d'articles ("## DEBUT DOC" et "## FIN DOC" dans "{corpus}_textbrut.txt").

Arg:
    Le nom du corpus (emea ou frwiki).
"""

import argparse


def get_liste_of_sentid(corpus):
    """
    Récupère la liste des sent_id par fichiers.
    """
    with open(f"z_fichiers_intermediaires/{corpus}_textbrut_annote.txt", "r") as file:
        liste_lignes = file.readlines()
    all_text = []
    for ligne in liste_lignes:
        if ligne[:12] == "## DEBUT DOC":
            new_text = []
        elif ligne.startswith(corpus):
            new_text.append(ligne.strip())
        elif ligne[:10] == "## FIN DOC":
            all_text.append(new_text)
    return all_text


def get_sents_dico():
    """
    Crée un dictionnaire avec les sent_id en clé et un tuple composé
    du texte de la phrase et de la phrase au format UD en valeur.
    """
    texte = ""
    files = ["z_corpus_initial/fr_sequoia-ud-dev.cupt",
             "z_corpus_initial/fr_sequoia-ud-test.cupt",
             "z_corpus_initial/fr_sequoia-ud-train.cupt"]
    for fic in files:
        with open(fic, "r") as filein:
            filein.readline()
            texte = texte + filein.read().strip()

    liste_sents = texte.split("\n\n")
    dico_sents = {}
    for sent_bloc in liste_sents:
        lignes = sent_bloc.split("\n")
        sent_id = lignes[0].split(" ")[-1]
        text = lignes[1]
        text = text.split(" = ")[1]
        dico_sents[sent_id] = (text, sent_bloc)
    return dico_sents


def main():
    """
    Crée des fichiers txt et cupt pour chaque article Wikipédia/EMEA.
    """
    parser = argparse.ArgumentParser(description="fichier")
    parser.add_argument("corpus", help="emea ou frwiki")
    args = parser.parse_args()
    corpus = args.corpus

    all_texts = get_liste_of_sentid(corpus)
    sents_dico = get_sents_dico()

    # Fichiers cupt
    i = 1
    for text in all_texts:
        filename = f'{corpus}_cupt/{corpus}_' + str(i) + '.cupt'
        with open(filename, "w") as fileout:
            fileout.write("# global.columns = ID FORM LEMMA UPOS XPOS FEATS"
                          " HEAD DEPREL DEPS MISC PARSEME:MWE\n")
            for sent_id in text:
                fileout.write(sents_dico[sent_id][1])
                fileout.write("\n\n")
        i += 1

    # Fichiers txt
    i = 1
    for text in all_texts:
        filename = f'{corpus}_txt/{corpus}_' + str(i) + '.txt'
        with open(filename, "w") as fileout:
            for sent_id in text:
                fileout.write(sents_dico[sent_id][0])
                fileout.write("\n")
        i += 1


if __name__ == "__main__":
    main()
