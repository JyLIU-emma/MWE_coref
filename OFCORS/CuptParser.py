#/usr/bin/python

#TODO: maintenant: 1 cupt -- 1 fichier; on a besoin de 1 cupt -- plusieurs fichier ?

from OfcorsFilesParser import *

class Cupt():

    def __init__(self, filepath):
        self.type = "cupt"  #########TODO
        self.lignes = {}
        numero_ligne = 0
        token_i = -1
        with open(filepath, encoding="utf8") as f:
            liste_lignes = f.readlines()
        for ligne in liste_lignes:
            if ligne[0] != "#" and ligne != "\n":
                cols = ligne.split("\t")
                no_token_sent = cols[0]
                token = cols[1]
                if "-" not in no_token_sent:
                    token_i += 1
                    self.lignes[numero_ligne] = Ligne(numero_ligne, str(token_i), ligne.strip(), token)
                else:
                    self.lignes[numero_ligne] = Ligne(numero_ligne, f"{token_i}-{token_i+1}", ligne.strip(), token)
            else:
                # pour ligne de commentaire: numéro de token : -1
                # TODO: peut etre elargir si on veut traiter sent_id, newdoc
                self.lignes[numero_ligne] = Ligne(numero_ligne, -1, ligne.strip())
            numero_ligne += 1
    
    def add_ofcors_output(self, ofcors_out):
        self.type = "cupt+coref"
        for ligne in self.lignes.values():
            if ligne.i_token == -1 or "-" in ligne.i_token:
                continue
            # print(type(ligne.i_token))

            token_coref = ofcors_out.tokens.get(ligne.i_token)
            if token_coref == None:
                token_coref_form = None
            else:
                token_coref_form = token_coref.text   #########TODO: Paris.
            if ligne.token_form == token_coref_form:
                # pour les commentaire : ligne.coref == None
                ligne.coref = token_coref.ment_coref_list
            else:
                print(f'Incohérence pour token "{ligne.token_form}" de ligne {ligne.indice}')
                break


class Ligne():
    def __init__(self, indice, i_token, content, token_form="#commentaire"):
        self.indice = indice
        self.i_token = i_token
        self.token_form = token_form
        self.content = content
        self.coref = {}   #dict or list?


if __name__ == "__main__":
    # exemple d'usage
    mention_file = "/Users/liujianying/Desktop/stage/MWE_coref/OFCORS/blabla/ofcors_outputs/blabla_mentions_output.json"
    mentions = Mentions(mention_file)

    coref_file = "/Users/liujianying/Desktop/stage/MWE_coref/OFCORS/blabla/ofcors_outputs/blabla_resulting_chains.json"
    coref = CorefChaines(coref_file)
    mentions.chainer(coref.ment_cluster)

    token_file = "/Users/liujianying/Desktop/stage/MWE_coref/OFCORS/blabla/ofcors_outputs/blabla_tokens.json"
    ofcors_out = OfcorsOutput(token_file)
    ofcors_out.merge_result(mentions)

    cupt_file = "./blabla/blabla.cupt"
    cupt = Cupt(cupt_file)
    cupt.add_ofcors_output(ofcors_out)

    for i_ligne, ligne in cupt.lignes.items():
        print(i_ligne, ligne.i_token, ligne.token_form, ligne.coref)


