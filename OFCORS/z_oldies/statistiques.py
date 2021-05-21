# -*- coding: utf-8 -*-
# Anaëlle Pierredon et Jianying Liu

"""
Production de statistiques sur la totalité des MWE des différents fichiers.
Argument : répertoire où se trouvent les cupt+
"""

import glob
import argparse

# -------------------------- CLASSES --------------------------


class ExprPoly():
    """
    Expressions polylexicales.
    """
    def __init__(self, identifiant, type_mwe, texte, tokens, coref, cas):
        self.identifiant = identifiant
        self.texte = texte
        self.tokens = [tokens]
        self.coref = [coref]
        self.type_mwe = type_mwe
        self.cas = cas


class TypeExpr():
    """
    Liste d'expressions polylexicales par type.
    """
    def __init__(self, type_mwe):
        self.type_mwe = type_mwe
        self.mwes = []


class Repertoire():
    """
    Une liste des MWEs globale et une liste des MWEs par type contenues
    dans tous les fichiers du répertoire.
    """

    def __init__(self, repertoire):
        self.repertoire = repertoire
        self.liste_phrases = self.lecture()

        self.liste_mwes = []
        for phrase in self.liste_phrases:
            self.liste_mwes.extend(phrase_mwe(phrase))

        self.liste_type = complet_type(self.liste_mwes)

    def lecture(self):
        """
        Lecture des fichiers.
        Entrée : entree, un nom de fichier
        sortie : filein, une liste des phrases du fichier
        """
        liste_phrases = []
        for fichier in glob.glob(f"{self.repertoire}*"):
            with open(fichier, 'r') as entree:
                sortie = entree.read().split('\n\n')
            liste_phrases.extend(sortie)
        return liste_phrases


# ----------------------- FONCTIONS (CONSTRUCTION) -----------------------


def phrase_mwe(phrase):
    """
    Liste des MWE par phrases

    Entrée : phrase, la liste des lignes de la phrase
    Sortie : liste_expoly, la liste des MWE de la phrase (ExprPoly())
    """
    liste_expoly = []

    for ligne in phrase.split('\n'):
        if ligne.startswith('# text'):
            texte = ligne.split(' = ')[1]
        if ligne.startswith("#") or ligne.strip() == "":
            continue
        ligne = ligne.strip().split('\t')
        mwes = ligne[10]
        if mwes != "*":
            for mwe in mwes.split(';'):
                infos = mwe.split(':')
                id_mwe = int(infos[0])
                if len(infos) == 2:
                    expoly = ExprPoly(id_mwe, infos[1], texte, ligne[1],
                                      ligne[12], "?")
                    liste_expoly.append(expoly)
                else:
                    for expoly in liste_expoly:
                        if expoly.identifiant == id_mwe:
                            expoly.tokens.append(ligne[1])
                            expoly.coref.append(ligne[12])
    return liste_expoly


def complet_type(liste_expoly):
    """
    Entrée : liste_expoly, la liste des MWE de la phrase (ExprPoly())
    Sortie : liste_typexp, la liste des types existants dans le fichier et
             les expressions polylexicales qui correspondent à ce type.
             (TypeExpr())
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
    Afficher les tokens, la coref et le cas par MWE classées selon leur type.
    """
    print("------------------------")
    for typexp in liste_typexp:
        print(typexp.type_mwe)
        for expoly in typexp.mwes:
            print(f"tokens : {expoly.tokens}, coref : {expoly.coref}, "
                  f"cas : {expoly.cas}")


def affichage_stats_globales(liste_typexp):
    """
    Afficher le nombre de MWE par type et le nombre de MWE total.
    """
    print("------------------------")
    total = 0
    for typexp in liste_typexp:
        print(f"{typexp.type_mwe} : {len(typexp.mwes)}")
        total += len(typexp.mwes)
    print(f"TOTAL : {total}")


def affichage_stats_coref(liste_typexp):
    """
    Afficher le nombre de MWE faisant partie d'une chaîne de coréférence
    par type et total.
    """
    print("------------------------")
    total = 0
    nb_coref_total = 0
    for typexp in liste_typexp:
        print(typexp.type_mwe)
        nb_coref = 0
        for expoly in typexp.mwes:
            total += len(typexp.mwes)
            coref = len([el for el in expoly.coref if el != "*"])
            if coref > 0:
                nb_coref += 1
                nb_coref_total += 1
                print(f"tokens : {expoly.tokens}, coref : {expoly.coref}, "
                      f"cas : {expoly.cas}")
        print(f"====>{nb_coref}/{len(typexp.mwes)}\n")
    print(f"TOTAL\n====>{nb_coref_total}/{total}\n")


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

    affichage_infos(repertoire.liste_type)
    affichage_stats_globales(repertoire.liste_type)
    affichage_stats_coref(repertoire.liste_type)


if __name__ == "__main__":
    main()
