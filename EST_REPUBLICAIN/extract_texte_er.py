# -*- coding: utf-8 -*-
# Jianying Liu, Anaëlle Pierredon

"""
Script pour diviser les fichiers xml du corpus Est Républicain en articles
permettre un simple fitrage par la taille (nombre de mots) de chaque article
résultat de sortie: un répertoire de txt et un json file

usage:
    python extract_texte_er.py rep_corpus taille [-f jsonfile]
Ayant déjà un json file:
    python extract_texte_er.py TXT2003 300 -f TXT2003.json
Ayant seulement le répertoire dézippé du corpus:
    python extract_texte_er.py TXT2003 400
"""

import re
import glob
import os
import json
import argparse


def get_files_content(dir_name):
    """
    Récupère le contenu des fichiers du répertoire.

    Args:
        dir_name (str), le nom du répertoire où se trouvent les fichiers
    Returns:
        all_texte (dict), avec comme clé le nom du fichier.txt et comme valeur
                          son contenu
    """
    files = glob.glob(f"{dir_name}/*.txt")
    all_texte = {}
    for file in files:
        # filename = re.sub(dir_name, "", file)
        with open(file, "r", encoding="utf8") as fic:
            text = fic.read()
        text = re.sub(r"<estRepublicain date=\".+\">", "", text)
        all_texte[file] = text
    return all_texte


def sep_texte(texte):
    """
    Sépare un fichier texte en autant d'articles qui le compose

    Args:
        texte (str), le contenu d'un fichier.txt
    Returns:
        dico (dict), avec comme clé le nom de l'article et en valeur son contenu
                     textuel
    """
    articles = texte.split("\n\n")
    dico = {}
    for article in articles:
        match = re.search(r"<head>(.+)</head>", article)
        if match:
            titre = match.group(1)
            texte = re.sub(r"<head>(.+)</head>", "", article)
            texte = texte.strip()
            if texte != "":
                dico[titre] = texte
    return dico


def create_files_json(dir_name):
    """
    Crée un fichier json avec des informations (date, titre, contenu,
    nombre de mots) sur tous les articles des fichiers.txt du répertoire
    donné en argument.

    Args:
        dir_name (str), le nom du répertoire où se trouvent les fichiers
    Returns:
        all_json (dict), pour chaque article un dictionnaire avec sa date, son
                         titre, son contenu et son nombre de mots.
    """
    all_texte = get_files_content(dir_name)
    all_json = {}
    i = 1
    for filename, text in all_texte.items():
        # each file name
        date = filename.split("/")[-1]
        date = date[:-4]
        articles = sep_texte(text)
        # each article in each file
        for titre, contenu in articles.items():
            num_word = len(contenu.split())
            all_json[i] = {"date": date, "titre": titre, "contenu": contenu,
                           "nombre_mots": num_word}
            i += 1
    with open(f"{dir_name}.json", "w", encoding="utf8") as jsonfile:
        jsonfile.write(json.dumps(all_json, indent=4))
    return all_json


def json_to_dir(jsonfile, dir_name, article_length=0, file=False):
    """
    Crée un répertoire avec un fichier pour chaque article ayant un nombre de
    mots supérieur à article_length.

    Args:
        jsonfile (str ou dict), le nom du fichier json s'il existe,
            le dictionnaire contenant les infos sur tous les articles sinon
        dir_name (str), le nom du répertoire où se trouvent les fichiers
        article_length (int), le nombre minimal requis de mots dans un article
        file (bool), True si le fichier.json existe déjà, False sinon
    """
    if file:
        with open(jsonfile, encoding="utf8") as fic:
            dico_all = json.load(fic)
    else:
        dico_all = jsonfile
    # create folder
    path = dir_name + "_articles"
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    print(f"Répertoire des articles: {path}")
    compteur_article = 0
    for id_art, article in dico_all.items():
        if article['nombre_mots'] >= article_length:
            with open(f"{path}/{article['date']}_{id_art}.txt", "w", encoding="utf8") as fileout:
                fileout.write(article['titre'] + '\n' + article['contenu'])
            compteur_article += 1
    print(f"Nombre d'articles dans le répertoire: {compteur_article}")


def main():
    """
    Divise les fichiers xml du corpus Est Républicain en articles et ne garde
    que les articles de la taille donnée en argument.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("inputdir", help="Chemin vers le répertoire d'entrée")
    parser.add_argument("minlength", help="Taille minimale de chaque article", type=int)
    parser.add_argument("-f", "--jsonfile", help="chemin vers le fichier json déjà créé")
    args = parser.parse_args()
    inputdir = args.inputdir
    length = args.minlength
    jsonfile = args.jsonfile
    outputdir = f"{inputdir}_len{length}"

    if jsonfile:
        json_to_dir(jsonfile, outputdir, length, file=True)
    else:
        dico = create_files_json(inputdir)
        json_to_dir(dico, outputdir, length)


if __name__ == "__main__":
    main()
