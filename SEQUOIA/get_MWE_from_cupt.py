import re
import json

def restructurer_cupt(fichier_input):
    with open(fichier_input) as f:
        text = f.read()
    text = re.sub("# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC PARSEME:MWE\n","",text.strip())
    liste_sents = text.split("\n\n")

    liste_sent_sortie = []

    for sent in liste_sents:
        lignes = sent.split("\n")
        source_sent_id = re.match(r"# source_sent_id = (.+)", lignes[0])
        source_sent_id = source_sent_id.group(1)
        text_sent = re.match(r"# text = (.+)", lignes[1])
        text_sent = text_sent.group(1)

        dico_mwe = {}  # dico interne de phrase
        for token_line in lignes[2:]:
            token_info_liste = token_line.split("\t")
            id_token = token_info_liste[0]
            form_token = token_info_liste[1]
            lemme_token = token_info_liste[2]
            MWE_token = token_info_liste[10]

            # traitement de colonne MWE
            col_sep = MWE_token.split(";")
            for mark_mwe in col_sep:
                if mark_mwe == "*":
                    continue
                elif ":" in mark_mwe:
                    id_mwe = mark_mwe.split(":")[0]
                    type_mwe = mark_mwe.split(":")[1]
                    dico_mwe[id_mwe]={"type":type_mwe, "tokens_list":[form_token]}
                else:
                    dico_mwe[mark_mwe]["tokens_list"].append(form_token)
        if dico_mwe != {}:
            liste_sent_sortie.append({"sent_id":source_sent_id, "text":text_sent, "MWE":dico_mwe})
    return liste_sent_sortie


fic1 = "fr_sequoia-ud-test.cupt"
fic2 = "fr_sequoia-ud-dev.cupt"
fic3 = "fr_sequoia-ud-train.cupt"
l1 = restructurer_cupt(fic1)
l2 = restructurer_cupt(fic2)
l3 = restructurer_cupt(fic3)
l = l1 + l2 + l3

# voir la structure de cette liste de phrases
with open("MWE_decompte.json","w") as f:
    f.write(json.dumps(l, indent=4))

def get_one_type_mwe_list(liste_sents_sortie, type_mwe):
    all_mwe = []
    liste_one_type = []
    for sent in liste_sents_sortie:
        mwes = sent["MWE"]
        for i in mwes.values():
            all_mwe.append({"content":i["tokens_list"], "type":i["type"], "contexte_sent":sent["text"]})


    for i in all_mwe:
        if i["type"] == type_mwe:
            liste_one_type.append(i)
    return liste_one_type, len(all_mwe)

types_mwe = ['VID', 'IRV', 'LVC.full', 'LVC.cause', 'MVC']
for t in types_mwe:
    liste_one_type, len_all = get_one_type_mwe_list(l, t)
    print(t, ":", len(liste_one_type))
    with open(f"MWE_decompte_{t}.json","w") as f:
        f.write(json.dumps(liste_one_type, indent=4))
print("total MWE:", len_all)
