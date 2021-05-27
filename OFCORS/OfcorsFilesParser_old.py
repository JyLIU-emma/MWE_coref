# -*- coding: utf-8 -*-
# Jianying Liu et Anaëlle Pierredon
"""
parser et unifier les 3 fichiers sorties de l'OFCORS
"""
import json


class Mention():
    """
    La classe contient tous les infos d'une mention:

    Attributes:
        content (list): une liste de ses tokens text
        start (int): l'indice de son premier token
        end (int): l'indice de son dernier token
        mid (str): l'id de mention dans fichier mention_output (commence par 1)
        span (list): une liste des indice de tous les tokens dans cette mention
        is_coref (bool): montrer si une mention est dans une chaîne de
            coréférence, False par défaut
        chaine_id (str): l'id de la chaîne qu'il fait partie
    """
    def __init__(self, content, start, end, mid):
        self.content = content
        self.start = int(start)  # 4
        self.end = int(end)  # 6
        self.mid = mid
        self.span = [i for i in range(self.start, self.end+1)]  # [4,5,6]
        self.is_coref = False
        self.chaine_id = ""


class Token():
    """
    La classe d'un token pour la sortie de l'ofcors

    Attributes:
        text (str): texte de ce token
        i_ofcors (str): l'indice de token distribuée par l'ofcors (debut 0)
        is_mention (bool): montre si le token fait partie d'une mention
        ment_list (list): une liste des Mention objets liés à ce token
        ment_coref_list (dict):
            un dictionnaire des dict contenant l'id de mention, l'id de coref
            clé dans le dict: ment_id,   valeur: ment_id, coref_id
    """
    def __init__(self, i_ofcors, text):
        self.text = text
        self.i_ofcors = i_ofcors
        self.is_mention = False
        self.ment_list = []  # Mention object
        self.ment_coref_list = {}  # 0:1; 0:2 ==>  {"1":{ment_id:"1", coref_id:"0"},"2":{ment_id:"2", coref_id:"0"}}


class Mentions():
    """
    Classe sert à initialiser les informatons
    à partir du fichier mentions_output.json de l'ofcors.
    Elle lie les infos des chaînes de coréférences à chaque mention.

    Attributes:
        tokens (dict): un dictionnaire liste tous les tokens
        qui fait partie d'une mention.
            clé: id de token, valeur: liste des id de mention
        mentions (dict): dictionnaire de Mention objet
    """
    def __init__(self, filepath):
        """
        Initialiser l'info dans le fichier
        Args:
            filepath (str): chemin vers ce fichier
        """
        self.tokens = {}
        self.mentions = {}
        with open(filepath, encoding="utf8") as mentions_file:
            text = mentions_file.read()
        dico_mentions = json.loads(text)
        for cle, ment in dico_mentions.items():
            mention = Mention(ment["CONTENT"], ment["START"], ment["END"], cle)
            self.mentions[mention.mid] = mention
        self.tokens2mentions()

    def chainer(self, dico_chaine):
        """
        Ajouter l'info de chaîne de coréférence dans Mention objet
        Args:
            dico_chaine (dict): dict mentions(clé, str)<-->chaine(valeur, str)
        """
        for mention in self.mentions.values():
            mention.chaine_id = dico_chaine.get(mention.mid, "")
            if mention.chaine_id != "":
                mention.is_coref = True

    def tokens2mentions(self):
        """
        Restructuer les infos, remplir dico Mentions.tokens,
        utilisé seulement à l'intérieur
        """
        for mention in self.mentions.values():
            for i_token in mention.span:
                if str(i_token) not in self.tokens.keys():
                    self.tokens[str(i_token)] = [mention.mid]
                else:
                    self.tokens[str(i_token)].append(mention.mid)


class CorefChaines():
    """
    Classe sert à initialiser les informatons
    à partir du fichier resulting_chains.json de l'ofcors.

    Attributes:
        ment_cluster (dict): dictionnaire ayant
            clef: l'id de mention  valeur: l'id de chaine de coréférence
        clusters (dict): prendre la valeur de la clé "clusters" du fichier
    """

    def __init__(self, filepath, file=True):
        """
        Initialiser les infos et les remplir dans l'objet

        Args:
            filepath (str):
                1) chemin vers le fichier resulting_chains,json
                2) le contenu du fichier resulting_chains.json, même structure
                    forme: dict
            file (bool): mettre à False si l'entrée est le contenu
        """
        self.ment_cluster = {}
        self.clusters = {}
        if file:
            with open(filepath, encoding="utf8") as chaines_file:
                text = chaines_file.read()
            dico_json = json.loads(text)
        else:
            dico_json = filepath

        if dico_json["clusters"] != {}:
            self.clusters = dico_json.get("clusters")
            for no_cluster, ments in self.clusters.items():
                for id_mention in ments:
                    self.ment_cluster[id_mention] = no_cluster
            self.has_coref = True
        else:  # TODO: need or not?
            self.has_coref = False


class OfcorsOutput():
    """
    Classe sert à fusionner tous les sortie de l'ofcors.

    Attributes:
        tokens (dict): un dictionnaire des Token objets, clef: id
    """

    def __init__(self, filepath):
        """
        Args:
            filepath (str): chemin vers fichier tokens.json de l'ofcors
        """
        self.tokens = {}
        with open(filepath, encoding="utf8") as tokens_file:
            text = tokens_file.read()
        dico_json = json.loads(text)
        for i, t_form in dico_json.items():
            token = Token(i, t_form)
            self.tokens[i] = token

    def merge_result(self, mentions):
        """
        fussionner le résultat de l'ofcors dans cette liste des tokens.
        Args:
            mentions (Mentions): l'objet Mentions contenant l'info de coréf
        """
        for token in self.tokens.values():
            if token.i_ofcors in mentions.tokens.keys():
                token.is_mention = True
                ment_ids = mentions.tokens[token.i_ofcors]
                for ment_id in ment_ids:
                    mention = mentions.mentions[ment_id]
                    token.ment_list.append(mention)
                # token.ment_coref_list = [{"ment_id":ment.mid, "coref_id":ment.chaine_id} for ment in token.ment_list]
                    token.ment_coref_list[ment_id] = {"ment_id": mention.mid, "coref_id": mention.chaine_id}

def main():
    """
    exemple d'usage
    """

    mention_file = "./blabla/ofcors_outputs/blabla_mentions_output.json"
    mentions = Mentions(mention_file)
    # print(mentions.mentions[1].span)
    # for token_id, mention in mentions.tokens.items():
    #     print(token_id, mention)

    print("-"*30)

    coref_file = "./blabla/ofcors_outputs/blabla_resulting_chains.json"
    coref = CorefChaines(coref_file)
    # print(coref.ment_cluster)
    # print(coref.clusters['0'])
    # print(coref.has_coref)
    mentions.chainer(coref.ment_cluster)
    # print(mentions.mentions[22].mid, mentions.mentions[22].chaine_id)

    print("-"*30)

    token_file = "./blabla/ofcors_outputs/blabla_tokens.json"
    ofcors_out = OfcorsOutput(token_file)
    ofcors_out.merge_result(mentions)

    for indice, token in ofcors_out.tokens.items():
        print(indice, token.i_ofcors, token.text,
              [ment.mid for ment in token.ment_list], token.ment_coref_list)

if __name__ == "__main__":
    main()
