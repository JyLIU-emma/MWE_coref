import re
import glob
import os
import json
import argparse

def get_files_content(dir_name):
    files = glob.glob(f"{dir_name}/*.txt")
    all_texte = {}
    for f in files:
        # filename = re.sub(dir_name, "", f)
        with open(f, "r", encoding="utf8") as fic:
            text = fic.read()
        text = re.sub(r"<estRepublicain date=\".+\">", "", text)
        all_texte[f] = text      
    return all_texte

def sep_texte(texte):
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
            all_json[i] = {"date":date, "titre":titre, "contenu": contenu, "nombre_mots": num_word}
            i += 1
    with open(f"{dir_name}.json", "w", encoding="utf8") as jsonfile:
        jsonfile.write(json.dumps(all_json, indent=4))  
    return all_json

def json_to_dir(jsonfile, dir_name, article_lenth=0, file=False):
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
    for id, article in dico_all.items():
        if article['nombre_mots'] >= article_lenth:
            with open(f"{path}/{article['date']}_{id}.txt", "w", encoding="utf8") as fileout:
                fileout.write(article['titre'] + '\n' + article['contenu'])
            compteur_article += 1
    print(f"Nombre d'articles dans le répertoire: {compteur_article}")




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputdir", help="le chemin vers le répertoire d'entrée")
    parser.add_argument("minlenth", help="La taille minimale de chaque article", type=int)
    parser.add_argument("-f", "--jsonfile", help="chemin vers le fichier json déjà créé")
    args = parser.parse_args()
    inputdir = args.inputdir
    lenth = args.minlenth
    jsonfile = args.jsonfile
    outputdir = f"{inputdir}_len{lenth}"

    if jsonfile:
        json_to_dir(jsonfile, outputdir, lenth, file=True)
    else:
        dico = create_files_json(inputdir)
        json_to_dir(dico, outputdir, lenth)

if __name__ == "__main__":
    main()