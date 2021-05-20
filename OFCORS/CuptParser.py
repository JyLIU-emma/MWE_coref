#/usr/bin/python

#TODO: maintenant: 1 cupt -- 1 fichier; on a besoin de 1 cupt -- plusieurs fichier ?
import re
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
            if ligne.i_token == -1 or "-" in ligne.i_token: #si c'est u commentaire ou au/du
                continue

            token_coref = ofcors_out.tokens.get(ligne.i_token)  # Token objet
            if token_coref != None:   # None : mot pas dans sortie ofcors (mot non mention)
                token_coref_form = token_coref.text
                token_coref_form = re.sub(r"(.+)[\.,:;\"]$", "\\1", token_coref_form) #traiter ponctuation collé après token, e.g.: Paris.
                if ligne.token_form == token_coref_form:
                    # pour les commentaire : ligne.coref == None
                    ligne.coref = token_coref.ment_coref_list
                    ligne.token_ofcors = token_coref
                else:
                    print(f'Incohérence pour token "{ligne.token_form}" de ligne {ligne.indice}')
                    break
    
    def write_to_file(self, filepath):
        # if self.type == "cupt":   ##########
        nombre_ligne = len(self.lignes)
        with open(filepath, "w") as file_out:
            for ligne in self.lignes.values():
                if ligne.i_token != -1 :  #c'est un token
                    # token n'est pas une mention
                    if ligne.coref == {}:
                        print(ligne.content + "\t*\t*", file=file_out)                    
                    # token est une mention
                    else:
                        # ajouter la colonne de mentions
                        ment_list = ligne.token_ofcors.ment_list
                        ligne.content = ligne.content + "\t" + ";".join([m.id for m in ment_list])

                        # ajouter la colonne de coreference
                        col_coref = [f"{mention['coref_id']}:{m_id}" for m_id, mention in ligne.coref.items() if mention['coref_id'] !='']
                        if col_coref == []:
                            ligne.content = ligne.content + "\t*"
                        else:
                            col_coref = ";".join(col_coref)
                            ligne.content = ligne.content + "\t" + col_coref
                        print(ligne.content, file=file_out)
                else:
                    if ligne.indice == 0:
                        ligne.content = ligne.content + " MENTION COREF"
                    print(ligne.content, file=file_out)


class Ligne():
    def __init__(self, indice, i_token, content, token_form="#commentaire"):
        self.indice = indice
        self.i_token = i_token
        self.token_form = token_form
        self.token_ofcors = None
        self.content = content
        self.coref = {}  #dict de dict (ment--coref)

        self.is_token = False if self.i_token == -1 else True


if __name__ == "__main__":
    # exemple d'usage
    print("#"*30)
    mention_file = "./blabla/ofcors_outputs/blabla_mentions_output.json"
    mentions = Mentions(mention_file)

    coref_file = "./blabla/ofcors_outputs/blabla_resulting_chains.json"
    coref = CorefChaines(coref_file)
    mentions.chainer(coref.ment_cluster)

    token_file = "./blabla/ofcors_outputs/blabla_tokens.json"
    ofcors_out = OfcorsOutput(token_file)
    ofcors_out.merge_result(mentions)

    cupt_file = "./blabla/blabla.cupt"
    cupt = Cupt(cupt_file)
    cupt.add_ofcors_output(ofcors_out)
    cupt.write_to_file("./blabla/test_out.cuptmc")

    # for i_ligne, ligne in cupt.lignes.items():
    #     print(i_ligne, ligne.i_token, ligne.token_form, ligne.coref)


