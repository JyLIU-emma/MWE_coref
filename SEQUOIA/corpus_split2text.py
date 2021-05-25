# -*- coding: utf-8 -*-
# Jianying LIU

def get_liste_of_sentid():
    with open("frwiki_textbrut.txt","r") as f:
        liste_line = f.readlines()
    all_text = []
    for ligne in liste_line:
        if ligne[:12] == "## DEBUT DOC":
            new_text = []
        elif ligne[:6] == "frwiki":
            new_text.append(ligne.strip())
        elif ligne[:10] == "## FIN DOC":
            all_text.append(new_text)
    return all_text

def get_sents_dico():
    texte = ""
    files = ["fr_sequoia-ud-dev.cupt","fr_sequoia-ud-test.cupt","fr_sequoia-ud-train.cupt"]
    for fic in files:
        with open(fic,"r") as f:
            f.readline()
            texte = texte + f.read().strip()

    liste_sents = texte.split("\n\n")
    dico_sents = {}
    for sent_bloc in liste_sents:
        lignes = sent_bloc.split("\n")
        sent_id = lignes[0].split(" ")[-1]
        text = lignes[1]
        text = text.split(" = ")[1]
        dico_sents[sent_id] = (text, sent_bloc)
    return dico_sents



all_texts = get_liste_of_sentid()
sents_dico = get_sents_dico()

i = 1
for text in all_texts:
    filename = 'frwiki/frwiki_' + str(i) +'.cupt'
    with open(filename,"w") as f:
        f.write("# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC PARSEME:MWE")
        for sent_id in text:
            f.write(sents_dico[sent_id][1])
    i += 1

i = 1
for text in all_texts:
    filename = 'frwiki/frwiki_' + str(i) +'.cupt'
    with open(filename,"w") as f:
        f.write("# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC PARSEME:MWE\n")
        for sent_id in text:
            f.write(sents_dico[sent_id][1])
            f.write("\n\n")
    i += 1

i = 1
for text in all_texts:
    filename = 'frwiki/frwiki_' + str(i) +'.txt'
    with open(filename,"w") as f:
        for sent_id in text:
            f.write(sents_dico[sent_id][0])
            f.write("\n")
    i += 1