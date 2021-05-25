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
    def __init__(self, identifiant, type_mwe, texte, tokens, coref):
        self.identifiant = identifiant  # 1 ou 2 (par phrase)
        self.texte = texte  # Merci de me donner l'occasion de...
        self.tokens = [tokens]  # ['me', 'donner']
        self.coref = [coref]  # ['*', '3']
        self.type_mwe = type_mwe  # LVC.full
        self.schema_mwe = []  # ["*", "*", "1", "1", "*", "*", "*", "*", ...]
        self.schema_mention = []  # ["*", "*", "*", "1", "*", "*", "*", "*", ...]
        self.cas = ""

    def append_schemas(self, schema_mwe, schema_mention):
        for indice in schema_mwe:
            liste_indices = [element.split(":")[0] for element in indice.split(";")]
            if str(self.identifiant) not in liste_indices:
                # Ce n'est pas la MWE qu'on est en train de définir
                self.schema_mwe.append("*")
            else:
                self.schema_mwe.append('1')

        self.schema_mention.extend(schema_mention)  #TODO utiliser les mentions écrites dans self.coref ?

        if len(list(set(self.coref))) == 1 and self.coref[0] == "*":  # ['*', '*']
            self.cas = "None"
        else:
            self.cas = self.determiner_cas()

        # print(self.texte)
        # print(f"MWE :\t\t{self.schema_mwe}")
        # print(f"MENTIONS :\t{self.schema_mention}")
        # print(f"CAS : {self.cas}\n\n")

    def determiner_cas(self):
        encours = False
        for num, (mwe, actuel) in enumerate(zip(self.schema_mwe,
                                            self.schema_mention)):

            # DEBUT DE MWE
            if mwe != '*'and not encours:  #TODO cas pas très bien géré à vérifier :  mwe 1, *, *, *, 1
                encours = True
                prec = self.schema_mention[num-1]
                if (prec and actuel) != '*' and prec == actuel: #TODO cas pas géré : mention 3;4 puis 3 ...
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
                prec = self.schema_mention[num-1]
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
                elif (debut == 1 and fin == 0) or (debut == 0 and fin == -1): #TODO mention :  * 1 1 * et mwe : 1 1 1 1
                    cas = "3"
                else:
                    cas = "4"
                return cas

        return "None"


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

    for expoly in liste_expoly:
        expoly.append_schemas(schema_mwe, schema_mention)

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
    print("-"*30)
    for typexp in liste_typexp:
        print(typexp.type_mwe)
        for expoly in typexp.mwes:
            print(f"tokens : {expoly.tokens}, coref : {expoly.coref}, "
                  f"cas : {expoly.cas}")


def affichage_stats_globales(liste_typexp):
    """
    Afficher le nombre de MWE par type et le nombre de MWE total.
    """
    print("-"*30)
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
    print("-"*30)
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
