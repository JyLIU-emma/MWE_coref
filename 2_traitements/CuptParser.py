# /usr/bin/python3
# Jianying Liu et Anaëlle Pierredon

"""
A COMPLÉTER

TODO: maintenant: 1 cupt -- 1 fichier; besoin de 1 cupt -- plusieurs fichier ?
"""

import re
from OfcorsFilesParser import Mentions, CorefChaines, OfcorsOutput


class Cupt():
    """
    Classe sert à parser fichier cupt

    Attributes:
        type (str): "cupt" ou "cupt+coref", défini automatiquement par script
        lignes (dict): un dictionnaire d'objets Ligne regroupant toutes infos
            clé (int): l'indice de ligne
            valeur (Ligne)
        tokens (dict): une liste des tokens de tout le fichier
            clé (str): indice redéfinie pour chaque token,
            unique dans un seul fichier cupt;
            pour MWT, e.g. du de le, seulement "du" a une indice.
            valeur (dict): stocker la forme de token et
            ses composants s'il est un MWT (sinon liste vide), exemple:
            {'token': 'au', 'MWT': ['à', 'le']}
    """
    def __init__(self, filepath):
        """
        Initialiser l'objet à partir d'un fichier cupt
        Args:
            filepath (str): chemin vers le fichier cupt
        """
        self.type = "cupt"  # TODO
        self.lignes = {}
        self.tokens = {}  # NEW_V2
        numero_ligne = 0
        token_i = -1
        with open(filepath, encoding="utf8") as filein:
            liste_lignes = filein.readlines()
        token_repete = []  # NEW_V2 liste pour stocker les id comme 2-4
        for ligne in liste_lignes:
            if ligne[0] != "#" and ligne != "\n":
                cols = ligne.split("\t")
                no_token_sent = cols[0]
                token = cols[1]
                # NEW_V2
                if no_token_sent in token_repete:
                    token_repete.remove(no_token_sent)
                    self.tokens[str(token_i)]["MWT"].append(token)    # NEW_V3 add token of MWT in liste
                else:
                    token_i += 1
                    self.tokens[str(token_i)] = {"token_form": token, "MWT": [], "indice_cupt": no_token_sent}  # NEW_V3  forme exemple pour un token: {'token': 'au', 'MWT': ['à', 'le']}

                self.lignes[numero_ligne] = Ligne(numero_ligne, str(token_i), ligne.strip(), token)

                # stocker les 2 lignes suivantes répétés
                match_index = re.match(r"^([0-9]+)-([0-9]+)$", no_token_sent)
                if match_index:
                    token_repete = [str(i) for i in range(int(match_index.group(1)), int(match_index.group(2))+1)]  # permet plus de 2 indices
            else:
                # pour ligne de commentaire: numéro de token : -1
                # TODO: peut etre elargir si on veut traiter sent_id, newdoc
                self.lignes[numero_ligne] = Ligne(numero_ligne, -1, ligne.strip())
            numero_ligne += 1

    def add_ofcors_output(self, ofcors_out):
        """
        Fusionner la sortie de l'ofcors dans notre Cupt objet selon l'indice
        de token. Tester en même temps la forme de token pour vérifier c'est
        les mêmes tokens.

        Args:
            ofcors_out (OfcorsOutput)
        """
        self.type = "cupt+coref"
        for ligne in self.lignes.values():
            if ligne.i_token == -1:  # NEW_V2
                continue
            token_coref = ofcors_out.tokens.get(ligne.i_token)  # Token objet
            if token_coref is not None:   # None : mot pas dans sortie ofcors (mot non mention)
                ligne.coref = token_coref.ment_coref_list
                ligne.token_ofcors = token_coref

    def write_to_file(self, filepath):
        """
        Écrire l'info dans Cupt objet complétée par la sortie Ofcors dans un
        fichier.

        Args:
            filepath (str) : chemin vers fichier sortie
        """
        # TODO: Spécifier cette fonction à cupt? (pas cupt+)
        with open(filepath, "w") as file_out:
            for ligne in self.lignes.values():
                # c'est un token
                if ligne.i_token != -1:
                    # token n'est pas une mention
                    if ligne.coref == {} or re.search(r"^([0-9]+)-([0-9]+)$", ligne.content.split('\t')[0]):  # NEW_A1 : pas d'annotation sur le contracté
                        print(ligne.content + "\t*\t*", file=file_out)
                    # token est une mention
                    else:
                        # ajouter la colonne de mentions
                        ment_list = ligne.token_ofcors.ment_list
                        ligne.content = ligne.content + "\t" + ";".join([m.mid for m in ment_list])

                        # ajouter la colonne de coreference
                        col_coref = [f"{mention['coref_id']}: {m_id}" for m_id, mention in ligne.coref.items() if mention['coref_id'] != '']
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
        indice (int): l'indice de cette ligne dans tout le fichier, début à 0
        i_token (str): l'indice du token, -1 pour tous les lignes non-token
        token_form (str): forme de token sur 2e colonne, sera "#commentaire"
            si la ligne est une ligne de commentaire/ligne vide
        token_ofcors (Token): None par défaut
        content (str): contenu de toute la ligne
        coref (dict): dictionnaire des dict de mention_id et sa chaine_id
        is_token (bool): montre si c'est une ligne de commentaire/ligne vide,
        ou une de token
    """
    def __init__(self, indice, i_token, content, token_form="#commentaire"):
        self.indice = indice
        self.i_token = i_token
        self.token_form = token_form
        self.token_ofcors = None
        self.content = content
        self.coref = {}  # dict de dict (ment--coref)
        self.is_token = False if self.i_token == -1 else True


def merge_cupt_ofcors(cupt_file, token_file, mention_file, coref_file):
    """
    exemple d'usage
    """
    cupt = Cupt(cupt_file)

    # NEW PRINT
    # for key, value in cupt.tokens.items():
    #     print(key, value)

    ofcors_out = OfcorsOutput(token_file, cupt.tokens)
    mentions = Mentions(mention_file, ofcors_out)

    # NEW PRINT
    if mentions.ments_omis != {}:
        print("Mentions omises:")
        for i, ment in mentions.ments_omis.items():
            print(i, ":", ment["CONTENT"])

    coref = CorefChaines(coref_file)
    mentions.chainer(coref.ment_cluster)
    ofcors_out.merge_result(mentions)
    cupt.add_ofcors_output(ofcors_out)
    return cupt


def main2():
    """
    Tester dictionnaire Cupt.tokens
    """
    cupt_file = "./blabla/blabla_annote.config48.cupt"
    cupt = Cupt(cupt_file)
    print(cupt.tokens)

    # Cupt.tokens
    for key, value in cupt.tokens.items():
        print(key, value)

    # Cupt.lignes
    # for i_ligne, ligne in cupt.lignes.items():
    #     print(i_ligne, ligne.i_token, ligne.token_form, ligne.coref)


def main():
    """
    exemple d'usage
    """
    cupt_file = "./SEQUOIA_emea/emea_2.cupt"
    token_file = "./SEQUOIA_emea/ofcors_outputs/emea_2_tokens.json"
    mention_file = "./SEQUOIA_emea/ofcors_outputs/emea_2_mentions_output.json"
    coref_file = "./SEQUOIA_emea/ofcors_outputs/emea_1_resulting_chains.json"
    cupt = merge_cupt_ofcors(cupt_file, token_file, mention_file, coref_file)
    cupt.write_to_file("./a_debug_test.cuptmc")

    # cupt_file = "./SEQUOIA_frwiki/frwiki_1.cupt"
    # token_file = "./SEQUOIA_frwiki/ofcors_outputs/frwiki_1_tokens.json"
    # mention_file = "./SEQUOIA_frwiki/ofcors_outputs/frwiki_1_mentions_output.json"
    # coref_file = "./SEQUOIA_frwiki/ofcors_outputs/frwiki_1_resulting_chains.json"
    # cupt = merge_cupt_ofcors(cupt_file, token_file, mention_file, coref_file)
    # cupt.write_to_file("./a_debug_test.cuptmc")


if __name__ == "__main__":
    main()
