# -*- coding: utf-8 -*-
# Anaëlle Pierredon et Jianying Liu

"""
Production de statistiques sur la totalité des MWEs des différents fichiers.
Args:
    Répertoire où se trouvent les cupt+
"""

import glob
import argparse

# -------------------------- CLASSES --------------------------


class ExprPoly():
    """
    Expressions polylexicales.

    Attributs:
        identifiant (int): Identifiant de la MWE dans la phrase (commence à 1)
        type_mwe (str): Type de la MWE (LVC.full, VID...)
        texte (str): Texte de la phrase où se trouve la MWE
        tokens (liste de str): Liste des tokens composant la MWE
        coref (liste de str): Appartenance ou non à une chaîne de coréférence
                              pour chaque token ("*" = pas dans une chaîne)
        schema_mwe (liste de str): Liste représentant les tokens de la phrase
                                - "*": ce token n'appartient pas à une MWE
                                - indice: ce token appartient à une MWE
        schema_mention (dict): représente les tokens de la phrase
                    - "*": token n'appartient pas à une mention de la chaine
                    - indice: token appartient à une mention de la chaine
                    Avec en clé la mention concernée
        cas (dict): Les différents cas possible de chevauchement ou d'inclusion
                   d'une mention dans une MWE avec en clé la mention concernée
        chaines (liste de dict): Les chaines de coreférences de la MWE
    """
    def __init__(self, identifiant, type_mwe, texte, tokens, coref):
        # Définis immédiatement
        self.identifiant = identifiant  # 1 ou 2 (par phrase)
        self.type_mwe = type_mwe  # LVC.full
        self.texte = texte  # Merci de me donner l'occasion de...
        self.tokens = [tokens]  # ['me', 'donner']
        self.coref = [coref]  # ['*', '3']

        # Définis plus tard
        self.schema_mwe = []  # ["*", "*", "1", "1", "*", "*", "*", "*", ...]
        self.schema_mention = {}  # {18: ["*", "*", "*", "18", "*", ...]}
        self.cas = {}  # {18: "1"}
        self.chaines = []

    def append_schemas(self, schema_mwe, schema_mention):
        """
        Ajoute des attributs schema_mwe, schema_mention et cas à partir des
        attributs déjà existants (identifiant et coref).
        """

        # Schema MWE
        for indice in schema_mwe:
            liste_indices = [element.split(":")[0] for element in indice.split(";")]
            if str(self.identifiant) not in liste_indices:
                # Ce n'est pas la MWE qu'on est en train de définir
                self.schema_mwe.append("*")
            else:
                self.schema_mwe.append('1')

        # Mentions
        coref = []
        for element in self.coref:
            if element != "*":
                coref.extend(element.split(";"))
        coref = list({element.split(':')[1] for element in coref if element != "*"})

        if len(set(coref)) > 0:  # tout sauf ["*", "*"]
            for ment_cor in coref:
                self.schema_mention[ment_cor] = []
                for ment_sch in schema_mention:
                    if ment_cor in ment_sch.split(';'):
                        self.schema_mention[ment_cor].append(ment_cor)
                    else:
                        self.schema_mention[ment_cor].append("*")
                self.cas[ment_cor] = self.determiner_cas(ment_cor)

        # VÉRIFICATIONS
        if len(set(coref)) > 0:
            print(self.texte)
            print(f"MWE :\n{self.schema_mwe}")
            print(f"MENTIONS ET CAS:")
            for mention in self.schema_mention:
                print(f"{mention}\t- {self.schema_mention[mention]}")
                print(f"  \t- {self.cas[mention]}\n")

    def append_chaine(self, dico_coref):
        """
        Ajoute l'attribut chaines.

        Args:
            dico_coref (dict): Toutes les chaînes du répertoire
        """
        for corefs in self.coref:
            if corefs != "*":
                for coref in corefs.split(";"):
                    id_coref = coref.split(":")[0]
                    if dico_coref[id_coref] not in self.chaines:
                        self.chaines.append(dico_coref[id_coref])

    def determiner_cas(self, ment):
        """
        Détermine le cas selon le chevauchement ou d'inclusion
        d'une mention dans une MWE.

        CAS 1 : La mention déborde de la MWE
        CAS 2 : La mention et la MWE sont identiques
        CAS 3 : La mention correspond à une partie de la MWE
        CAS 4 : MWE   =   se(1) faire(1) des(*) soucis(1)
                MENTION = se(*) faire(*) des(1) soucis(1)
        """
        schema_mention = self.schema_mention[ment]
        encours = False
        for num, (mwe, actuel) in enumerate(zip(self.schema_mwe,
                                                schema_mention)):

            # DEBUT DE MWE
            if mwe != '*'and not encours:  # TODO cas pas très bien géré à vérifier :  mwe 1, *, *, *, 1
                encours = True
                prec = schema_mention[num-1]
                if (prec and actuel) != '*' and prec == actuel:
                    # la mention commence avant : cas 1
                    debut = -1
                elif actuel not in (prec, '*'):
                    # la mention commence en même temps : cas 1, 2, 3
                    debut = 0
                elif (prec and actuel) == '*':
                    # la mention n'a pas encore commencé : cas 3, 4 ou rien
                    debut = 1

            # FIN DE MWE
            if (mwe == "*" and encours) or (mwe != "*" and num == len(self.schema_mwe)-1):
                encours = False
                prec = schema_mention[num-1]
                if prec == '*':
                    # la mention se fini avant/pas de mention : cas 3, 4, None
                    fin = -1
                elif prec != '*' and actuel == '*':
                    # la mention se fini en même temps : cas 1, 2, 3
                    fin = 0
                elif (prec and actuel) != '*':
                    # la mention n'est pas encore fini : cas 1 ou rien
                    fin = 1

                # Déterminer le cas
                if (debut == 0 and fin == 1) or (debut == -1 and fin == 0):
                    cas = "1"
                elif debut == 0 and fin == 0:
                    cas = "2"
                elif (debut == 1 and fin == 0) or (debut == 0 and fin == -1):  # TODO mention :  * 1 1 * et mwe : 1 1 1 1
                    cas = "3"
                else:
                    cas = "4"
                return cas

        return "None"


class TypeExpr():
    """
    Liste d'expressions polylexicales par type.

    Attributs:
        type_mwe (str): Type des MWEs (LVC.full, VID...)
        mwes (liste de ExprPoly): La liste des MWEs de ce type
    """
    def __init__(self, type_mwe):
        self.type_mwe = type_mwe
        self.mwes = []


class Repertoire():
    """
    Informations globales sur tous les fichiers du répertoire donné.

    Attributs:
        repertoire (str): le nom du répertoire
        liste_phrases (liste de str): liste des phrases de tous les fichiers
        liste_mwes (liste de ExprPoly): liste des MWEs de tous les fichiers
        chaines (dict): liste des chaines de coréférence de tous les fichiers
        liste_type (liste de TypeExpr): liste des MWEs par type
    """

    def __init__(self, repertoire):
        self.repertoire = repertoire
        self.liste_phrases = self.lecture()

        coref = {}
        self.liste_mwes = []
        for phrase in self.liste_phrases:
            mwes, coref = phrase_mwe(phrase, coref)
            self.liste_mwes.extend(mwes)

        self.chaines = coref
        self.liste_type = complet_type(self.liste_mwes)

    def lecture(self):
        """
        Lecture des fichiers.

        Returns:
            liste_phrases (liste de str), la liste des phrases de tous les
            fichiers du répertoire.
        """
        liste_phrases = []
        for fichier in glob.glob(f"{self.repertoire}*"):
            with open(fichier, 'r') as entree:
                sortie = entree.read().split('\n\n')
            liste_phrases.extend(sortie)
        return liste_phrases


# ----------------------- FONCTIONS (CONSTRUCTION) -----------------------


def phrase_mwe(phrase, dico_coref):
    """
    Liste des MWEs par phrases

    Args:
        phrase (str), les lignes de la phrase
        dico_coref (dict), les chaînes de coréférence trouvées dans les
                           phrases précédentes
    Returns:
        liste_expoly (liste de ExprPoly), la liste des MWEs de la phrase
        dico_coref (dict), complété par les nouvelles chaînes éventuelles
    """
    liste_expoly = []
    schema_mwe = []
    schema_mention = []

    for ligne in phrase.split('\n'):
        if ligne.startswith('# text'):
            texte = ligne.split(' = ')[1]
        if ligne.startswith("#") or ligne.strip() == "":
            continue
        ligne = ligne.strip().split('\t')
        mwes = ligne[10]
        mention = ligne[11]
        corefs = ligne[12]
        schema_mwe.append(mwes)
        schema_mention.append(mention)
        if mwes != "*":
            for mwe in mwes.split(';'):
                infos = mwe.split(':')
                id_mwe = int(infos[0])
                if len(infos) == 2:
                    expoly = ExprPoly(id_mwe, infos[1], texte, ligne[1],
                                      ligne[12])
                    liste_expoly.append(expoly)
                else:
                    for expoly in liste_expoly:
                        if expoly.identifiant == id_mwe:
                            expoly.tokens.append(ligne[1])
                            expoly.coref.append(ligne[12])
        if corefs != "*":
            for coref in corefs.split(';'):
                coref_id, coref_mention = coref.split(':')
                if coref_id not in dico_coref:
                    dico_coref[coref_id] = {}
                if coref_mention not in dico_coref[coref_id]:
                    dico_coref[coref_id][coref_mention] = []
                dico_coref[coref_id][coref_mention].append(ligne[1])

    for expoly in liste_expoly:
        expoly.append_schemas(schema_mwe, schema_mention)

    return liste_expoly, dico_coref


def complet_type(liste_expoly):
    """
    Args:
        liste_expoly (liste de ExprPoly), la liste des MWEs de la phrase
    Returns:
        liste_typexp (liste de TypeExpr), la liste des types existants et les
                    expressions polylexicales qui correspondent à ce type.
    """
    liste_typexp = list(set(expoly.type_mwe for expoly in liste_expoly))
    liste_typexp = [TypeExpr(type_mwe) for type_mwe in liste_typexp]

    for expoly in liste_expoly:
        for type_item in liste_typexp:
            if type_item.type_mwe == expoly.type_mwe:
                type_item.mwes.append(expoly)
    return liste_typexp


# ----------------------- FONCTIONS (AFFICHAGE) -----------------------


def affichage_infos(liste_typexp):
    """
    Affiche les tokens, la coref et le cas par MWE classées selon leur type.
    """
    print("-"*50)
    for typexp in liste_typexp:
        print(typexp.type_mwe)
        for expoly in typexp.mwes:
            print(f"tokens : {expoly.tokens}, coref : {expoly.coref}")


def affichage_stats_globales(liste_typexp):
    """
    Affiche le nombre de MWEs par type et le nombre de MWEs total.
    """
    print("-"*50)
    total = 0
    for typexp in liste_typexp:
        print(f"{typexp.type_mwe} : {len(typexp.mwes)}")
        total += len(typexp.mwes)
    print(f"TOTAL : {total}")


def affichage_stats_coref(liste_typexp):
    """
    Affiche le nombre de MWEs faisant partie d'une chaîne de coréférence par
    type et total, ainsi que les information sur ces MWEs (texte, tokens,
    coref, cas et chaines).
    """
    print("-"*50)
    total = 0
    nb_coref_total = 0
    for typexp in liste_typexp:
        print(typexp.type_mwe)
        total += len(typexp.mwes)
        nb_coref = 0
        for expoly in typexp.mwes:
            coref = len([el for el in expoly.coref if el != "*"])
            if coref > 0:
                nb_coref += 1
                nb_coref_total += 1
                print(f"\tTEXTE : {expoly.texte}")
                print(f"\tINFOS : tokens : {expoly.tokens}, "
                      f"coref : {expoly.coref}, cas : {expoly.cas}")
                print("\tCHAÎNE(S) : ")
                for chaine in expoly.chaines:
                    print(f"\t   -{chaine}")
                print("\n")
        print(f"==========>{nb_coref}/{len(typexp.mwes)}\n\n")
    print(f"TOTAL\n==========>{nb_coref_total}/{total}\n")


# --------------------------- MAIN ---------------------------


def main():
    """
    Créer une liste d'expressions polylexicales par type et afficher des
    statistiques.
    """
    parser = argparse.ArgumentParser(description="fichier")
    parser.add_argument("rep", help="répertoire des cupt+")
    args = parser.parse_args()

    repertoire = Repertoire(args.rep)

    for expoly in repertoire.liste_mwes:
        ExprPoly.append_chaine(expoly, repertoire.chaines)

    affichage_infos(repertoire.liste_type)
    affichage_stats_globales(repertoire.liste_type)
    affichage_stats_coref(repertoire.liste_type)


if __name__ == "__main__":
    main()
