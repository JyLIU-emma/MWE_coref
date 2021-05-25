# -*- coding: utf-8 -*-
# Jianying LIU

with open("frwiki.conllu","r") as f:
    liste_texte = f.readlines()
liste = []
for i in range(len(liste_texte)):
    if liste_texte[i][:9] == "# sent_id":
        sent_id = liste_texte[i].split(" = ")[1]
        sent = liste_texte[i+1].split(" = ")[1]
        liste.append((sent_id, sent))

with open("frwiki_textbrut.txt","w") as f:
    for sent_id, phrase in liste:
        print(sent_id+phrase, file=f)

