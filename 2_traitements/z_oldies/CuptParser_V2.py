#/usr/bin/python3
# Jianying Liu et Anaëlle Pierredon

#TODO: maintenant: 1 cupt -- 1 fichier; on a besoin de 1 cupt -- plusieurs fichier ?
import re
from OfcorsFilesParser import Mentions, CorefChaines, OfcorsOutput

class Cupt():
    """
    Classe sert à parser fichier cupt

    Attributes:
        type (str): "cupt" ou "cupt+coref", définit automatiquement par le script
        lignes (dict): un dictionnaire de Ligne objets regroupant tous les infos 
            clé (int): l'indice de ligne
            valeur (Ligne)
        tokens
    """
    def __init__(self, filepath):
        """
        Initialiser l'objet à partir d'un fichier cupt
        Args:
            filepath (str): chemin vers le fichier cupt
        """
        self.type = "cupt"  #########TODO
        self.lignes = {}
        self.tokens = {} #NEW
        numero_ligne = 0
        token_i = -1
        with open(filepath, encoding="utf8") as f:
            liste_lignes = f.readlines()
        token_repete = []  #NEW liste pour stocker les id comme 2-4
        for ligne in liste_lignes:
            if ligne[0] != "#" and ligne != "\n":
                cols = ligne.split("\t")
                no_token_sent = cols[0]
                token = cols[1]
                #NEW
                if no_token_sent in token_repete:
                    token_repete.remove(no_token_sent)
                else:
                    token_i += 1
                    self.tokens[str(token_i)] = token

                self.lignes[numero_ligne] = Ligne(numero_ligne, str(token_i), ligne.strip(), token)

                # stocker les 2 lignes suivantes répétés
                match_index = re.match(r"^([0-9]+)-([0-9]+)$", no_token_sent)
                if match_index:
                    token_repete = [match_index.group(1), match_index.group(2)]
                ###fin
                #OLD
                # if "-" not in no_token_sent:
                #     token_i += 1
                #     self.lignes[numero_ligne] = Ligne(numero_ligne, str(token_i), ligne.strip(), token)
                # else:
                #     self.lignes[numero_ligne] = Ligne(numero_ligne, f"{token_i}-{token_i+1}", ligne.strip(), token)
                ###fin
            else:
                # pour ligne de commentaire: numéro de token : -1
                # TODO: peut etre elargir si on veut traiter sent_id, newdoc
                self.lignes[numero_ligne] = Ligne(numero_ligne, -1, ligne.strip())
            numero_ligne += 1

    # def get_token_list(self):
    #     for ligne in self.lignes.values():
    #         if ligne.i_token != -1 or "-" not in

    def add_ofcors_output(self, ofcors_out):
        """
        Fusionner la sortie de l'ofcors dans notre Cupt objet selon l'indice de token.
        Tester en même temps la forme de token pour vérifier c'est les mêmes tokens.

        Args:
            ofcors_out (OfcorsOutput)
        """
        self.type = "cupt+coref"
        for ligne in self.lignes.values():
            if ligne.i_token == -1:  ##NEW
            # if ligne.i_token == -1 or "-" in ligne.i_token: #si c'est u commentaire ou au/du ##OLD
                continue

            token_coref = ofcors_out.tokens.get(ligne.i_token)  # Token objet
            if token_coref != None:   # None : mot pas dans sortie ofcors (mot non mention)
                # token_coref_form = token_coref.text
                # token_coref_form = re.sub(r"(.+)[\.,:;\"]$", "\\1", token_coref_form) #traiter ponctuation collé après token, e.g.: Paris.  mais Mr.   #####
                
                # TODO: token de cupt > token de ofcors    et    token de cupt < token de ofcors  ==unifier=> forme de token de cupt (token1(m1,c1), token2(m2,c2))
                # if ligne.token_form == token_coref_form:
                    # pour les commentaire : ligne.coref == None
                ligne.coref = token_coref.ment_coref_list
                ligne.token_ofcors = token_coref
                # else:
                    # print(f'Incohérence pour token "{ligne.token_form}" de ligne {ligne.indice}')
                    # break
    
    def write_to_file(self, filepath):
        """
        Écrire l'info dans Cupt objet complétée par la sortie Ofcors dans un fichier.

        Args:
            filepath (str) : chemin vers fichier sortie
        """
        #TODO: unifier traitement de ligne.content
        with open(filepath, "w") as file_out:
            for ligne in self.lignes.values():
                #c'est un token
                if ligne.i_token != -1 :
                    # token n'est pas une mention
                    if ligne.coref == {}:
                        print(ligne.content + "\t*\t*", file=file_out)                 
                    # token est une mention
                    else:
                        # ajouter la colonne de mentions
                        ment_list = ligne.token_ofcors.ment_list
                        ligne.content = ligne.content + "\t" + ";".join([m.mid for m in ment_list])

                        # ajouter la colonne de coreference
                        col_coref = [f"{mention['coref_id']}:{m_id}" for m_id, mention in ligne.coref.items() if mention['coref_id'] !='']
                        if col_coref == []:
                            ligne.content = ligne.content + "\t*"
                        else:
                            col_coref = ";".join(col_coref)
                            ligne.content = ligne.content + "\t" + col_coref
                        print(ligne.content, file=file_out)
                # c'est pas un token
                else:
                    if ligne.indice == 0:
                        ligne.content = ligne.content + " MENTION COREF"
                    print(ligne.content, file=file_out)


class Ligne():
    """
    Classe représentée chaque ligne.

    Attributes:
        indice (int): l'indice de cette ligne dans tout le fichier, commence par 0
        i_token (str): l'indice du token, -1 pour tous les lignes non-token
        token_form (str): forme de token sur 2e colonne, sera "#commentaire" si la ligne est une ligne de commentaire/ligne vide
        token_ofcors (Token): None par défaut
        content (str): contenu de toute la ligne
        coref (dict): dictionnaire des dict de mention_id et sa chaine_id
        is_token (bool): montre si c'est une ligne de commentaire/ligne vide, ou une de token 
    """
    def __init__(self, indice, i_token, content, token_form="#commentaire"):
        self.indice = indice
        self.i_token = i_token
        self.token_form = token_form
        self.token_ofcors = None
        self.content = content
        self.coref = {}  #dict de dict (ment--coref)
        self.is_token = False if self.i_token == -1 else True


def merge_cupt_ofcors(cupt_file, token_file, mention_file, coref_file):
    """
    exemple d'usage
    """
    cupt = Cupt(cupt_file)
    ofcors_out = OfcorsOutput(token_file, cupt.tokens)
    mentions = Mentions(mention_file, ofcors_out)
    coref = CorefChaines(coref_file)
    mentions.chainer(coref.ment_cluster)
    ofcors_out.merge_result(mentions)
    cupt.add_ofcors_output(ofcors_out)
    return cupt


def main():
    """
    exemple d'usage (ancien)
    """

    print("#"*30)
    mention_file = "./blabla/ofcors_outputs/blabla_mentions_output.json"
    coref_file = "./blabla/ofcors_outputs/blabla_resulting_chains.json"
    token_file = "./blabla/ofcors_outputs/blabla_tokens.json"
    cupt_file = "./blabla/blabla.cupt"
    output_file = "./blabla/test_out.cuptmc"

    mentions = Mentions(mention_file)

    coref = CorefChaines(coref_file)
    mentions.chainer(coref.ment_cluster)
 
    ofcors_out = OfcorsOutput(token_file)
    ofcors_out.merge_result(mentions)
    
    cupt = Cupt(cupt_file)
    cupt.add_ofcors_output(ofcors_out)
    cupt.write_to_file(output_file)

    # for i_ligne, ligne in cupt.lignes.items():
    #     print(i_ligne, ligne.i_token, ligne.token_form, ligne.coref)

def main2():
    """
    Tester dictionnaire tokens
    """
    cupt_file = "./blabla/blablaannote.config48.cupt"
    cupt = Cupt(cupt_file)
    print(cupt.tokens)

    # for i_ligne, ligne in cupt.lignes.items():
    #     print(i_ligne, ligne.i_token, ligne.token_form, ligne.coref)


def main3():
    """
    exemple d'usage
    """
    cupt_file = "./blabla/blablaannote.config48.cupt"
    token_file = "./blabla/ofcors_outputs/blabla_tokens.json"
    mention_file = "./blabla/ofcors_outputs/blabla_mentions_output.json"
    coref_file = "./blabla/ofcors_outputs/blabla_resulting_chains.json"
    cupt = merge_cupt_ofcors(cupt_file, token_file, mention_file, coref_file)
    cupt.write_to_file("./blabla/test_out.cuptmc")

if __name__ == "__main__":
    main3()