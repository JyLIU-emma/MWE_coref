# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Usage:
---
Mode train and test: s'assurer dans config.cfg que annotation_ONLY = False

python seen2seen.py

---
Mode annotation: s'assurer dans config.cfg que annotation_ONLY = True et
mettre le corpus dans INPUT/LANG/Nom_rep_corpus

python seen2seen.py Nom_rep_corpus
"""

import re
from itertools import product
import os
import glob
import sys
import ast
import itertools
from itertools import permutations
import time
import shutil
import collections
import statistics
from shutil import copyfile
import datetime
# import pandas as pd
from random import shuffle
import pickle
import configparser
from tqdm import tqdm
from seen2seen_STEP1_infosTrain import *
from seen2seen_STEP2_extractCands import *
from util_utilitaires import *
from util_cupt2typo_POS_dep_morpho import *
from util_distSyn import *
from util_cupt2Blind import *
from udpipe_annote import *


# ====================================


def obtentionCheminCorpus(languesAtraiter):
    allCorpusPaths = {}
    colonnesPOS = {}
    for langue in languesAtraiter:
        # Chemins vers les corpus
        allCorpusPaths[langue] = []
        pathTRAIN = str(repParent) + "/INPUT/" + str(langue) + "/" + str(corpusTRAIN)
        pathTRAIN = pathTRAIN.replace('"', '')
        allCorpusPaths[langue] = [pathTRAIN]
        pathDEV = str(repParent) + "/INPUT/" + str(langue) + "/" + str(corpusDEV)
        pathDEV = pathDEV.replace('"', '')
        if os.path.exists(str(pathDEV)):
            allCorpusPaths[langue] += [pathDEV]
        else:
            allCorpusPaths[langue] += ["noDEV"]
        pathTEST = str(repParent) + "/INPUT/" + str(langue) + "/" + str(corpusTEST)
        pathTEST = pathTEST.replace('"', '')
        allCorpusPaths[langue] += [pathTEST]
        # Choix de la colonne comportant les POS au format UD
        # ou à défaut les POS les plus détaillées
        (colonnePOS, nbPOScolXPOS) = whichPOScolumn(allCorpusPaths[langue][0])
        colonnesPOS[langue] = colonnePOS
        if colonnePOS == 4:
            modifColonne4(allCorpusPaths[langue][:-1])
    # Ajoute dans le fichier de config la colonne de POS qui sera prise en
    # compte pour chaque langue
    with open(str(repParent) + "/configAuto.cfg", "a") as f_config:
        copyfile(str(repParent) + "/config.cfg", str(repParent) + "/configAuto.cfg")
        f_config.write("\ncolonnesPOS = " + str(colonnesPOS))
    return allCorpusPaths, colonnesPOS


def NF2POSnorm_synthese(NF2POSnorm_details):
    dico = {}
    for langue in NF2POSnorm_details:
        dico[langue] = {}
        for NF in NF2POSnorm_details[langue]:
            for p in NF2POSnorm_details[langue][NF]:
                dico[langue][NF] = p
    return dico


def cupt2phrases(cupt):
    dicoPhrases = {}
    with open(cupt, "r") as f_cupt:
        infosCupt = f_cupt.readlines()
        corpusCupt = "".join(infosCupt[1:])
        phrases = corpusCupt.split("\n\n")[:-1]
        comptPhrase = 1
        for phrase in phrases:
            phraseHorsEntete = []
            lignes = phrase.split("\n")
            for ligne in lignes:
                if ligne[0] != "#":
                    infos = ligne.split("\t")
                    if "-" not in str(infos[0]):  # gestion amalgames
                        phraseHorsEntete.append(ligne)
            dicoPhrases[comptPhrase] = "\n".join(phraseHorsEntete)
            comptPhrase += 1
    return dicoPhrases


def FR_corrige_lemmatisation_IRV(NF_incorrecte, NF2categ):
    lemmes = NF_incorrecte.split(";")
    new_lemmes = []
    for lemme in lemmes:
        if lemme in ["me", "te", "nous", "vous", "lui"]:
            new_lemmes.append("se")
        else:
            new_lemmes.append(lemme)
    NF_corrigee = ";".join(sorted(new_lemmes))
    if NF_corrigee in NF2categ:
        return NF_corrigee
    else:
        new_lemmes2 = []
        for lemme in new_lemmes:
            if lemme == "le":
                new_lemmes2.append("se")
            else:
                new_lemmes2.append(lemme)
        NF_corrigee = ";".join(sorted(new_lemmes2))
        if NF_corrigee in NF2categ:
            return NF_corrigee
    return NF_incorrecte


def IT_corrige_lemmatisation_IRV(NF_incorrecte, NF2categ):
    lemmes = NF_incorrecte.split(";")
    new_lemmes = []
    for lemme in lemmes:
        if lemme in ["m'", "me", "mi", "vi", "s'", "te", "ti"]:
            new_lemmes.append("si")
        else:
            new_lemmes.append(lemme)
    NF_corrigee = ";".join(sorted(new_lemmes))
    if NF_corrigee in NF2categ:
        return NF_corrigee
    return NF_incorrecte


def NEW_localise_cands(dicoPhrases, dicoCands):
    localisation_candidat = []
    # localisation_cand = ""
    nbCand = 0
    for numPhrase in dicoCands:
        for NF in dicoCands[numPhrase]:
            for cand_string in dicoCands[numPhrase][NF]:
                cand = listeStr_2int(cand_string.split("|"))
                nbCand += 1
                tokensOrdreCroissant = ordonne_iterable(cand)
                # localisation_cand = str(numPhrase) + "_" + str(tokensOrdreCroissant)
                localisation_candidat.append((numPhrase, tokensOrdreCroissant))
    return localisation_candidat


def calcul_rappel(dicoCands, localisationMWE):
    nbTrouves = 0
    nbAtrouver = 0
    for phrase in localisationMWE:
        for NF in localisationMWE[phrase]:
            mwes = localisationMWE[phrase][NF]
            for mwe in mwes:
                nbAtrouver += 1
                if phrase in dicoCands:
                    if NF in dicoCands[phrase]:
                        cands = dicoCands[phrase][NF]
                        for cand in cands:
                            if cand == mwe:
                                nbTrouves += 1


def nbCands_extraits(dicoCands):
    compt = 0
    for phrase in dicoCands:
        for NF in dicoCands[phrase]:
            for cand in dicoCands[phrase][NF]:
                compt += 1
    return compt


def NEW_extract_cands(chemins, islanguecas, dico_NF2_case_morphoNoun, dico_seqPOS_perCat_POSnorm, NF2POSnormUnique, POSnorm2POSseq, nbMaxInsert, NF2categ, langue, NFs, nbInsertperNF, localisationMWE, NF2OrdreVerbes, stats_insertions, pronoms_VID_patron_PRON_PRON_VERB, filtres, dico_ImbricationsMWEs):
    cands_allcorpus = []
    # Candidate extraction in TRAIN
    repOut = str(repParent) + "/OUTPUT_seen/DEBUG/CANDIDATES/" + str(langue)
    if not os.path.exists(str(repOut)):
        os.makedirs(str(repOut))
    for corpus in range(0, len(chemins[langue])):
        if os.path.exists(chemins[langue][corpus]):  # and "noDEV" not in str(corpus):
            nomCorpus_split = chemins[langue][corpus].split("/")
            nomCorpus = nomCorpus_split[len(nomCorpus_split)-1]
            chemin_cands = str(repOut) + "/dicoCands_" + str(nomCorpus) + ".pickle"
            dicoPhrases = cupt2phrases(chemins[langue][corpus])  # indice 0 correspond au Train ### CHANGEMENT AllCorpusPath en chemins
            if not os.path.exists(str(chemin_cands)):
                dicoCands, dicoPOS = search_LemmaSeq(langue, chemins[langue][corpus], NFs, corpus)
                savepickle(dicoCands, str(repOut) + "/dicoCands_" + str(nomCorpus) + ".pickle")
                savepickle(dicoPOS, str(repOut) + "/dicoPOS_" + str(nomCorpus) + ".pickle")
            else:
                dicoCands = loadpickle(str(repOut) + "/dicoCands_" + str(nomCorpus) + ".pickle")
                dicoPOS = loadpickle(str(repOut) + "/dicoPOS_" + str(nomCorpus) + ".pickle")

            liste_NFs_cands_avant_filtrage = []
            for phrase in dicoCands:
                for NF in dicoCands[phrase]:
                    if NF not in liste_NFs_cands_avant_filtrage:
                        liste_NFs_cands_avant_filtrage.append(NF)
            dicoCands = generation_cands_parCombinaison(dicoCands)
            calcul_rappel(dicoCands, localisationMWE)
            if corpus == 0:
                dicoCandsTrain_avant_filtrage = {}
                dicoCandsTrain_avant_filtrage = dicoCands

            # ================================  filtrage des candidats =====================
            dicoPOSseq, dicoPOSnorm = NEW_tokens2_POSseq_POSnorm(dicoCands, dicoPOS, langue)

            NF2POSnorm = NF2POSnorm_synthese(NF2POSnormUnique)
            if filtres["f1"]:
                dicoCands = f1(dicoPOSnorm, dicoCands, NF2POSnorm)
            if filtres["f2"]:
                dicoPOSseq, dicoPOSnorm = NEW_tokens2_POSseq_POSnorm(dicoCands, dicoPOS, langue)
                dicoCands = f2(dicoCands, dicoPOSseq, POSnorm2POSseq)
            if filtres["f3"]:
                dicoCands = f3(dicoCands, dicoPOS, NF2categ, NF2POSnorm, dico_seqPOS_perCat_POSnorm)
            if filtres["f4"]:
                dicoCands = f4(dicoCands, NF2categ, stats_insertions)
            if filtres["f5"]:
                dicoCands = f5(dicoCands)
            if filtres["f6"]:
                dicoCands = f6(allCorpusPaths, chemins, dicoCands, dicoPhrases, dicoPOS, langue, corpus)
            if filtres["f7"]:
                dicoCands = f7(dicoCands, dicoPhrases, NF2categ, dico_NF2_case_morphoNoun, islanguecas)
            if filtres["f8"]:
                dicoCands = f8(dicoCands, dico_ImbricationsMWEs)
            cands_allcorpus.append(dicoCands)

    return cands_allcorpus


def liste_tuples_sorted_list(l):
    """
    input :  [(13, 4), (13, 12)]
    output : ['4|13', '12|13']
    """
    l_int = []
    l_out = []
    # tuples triés par ordre croissant de valeurs
    for t in l:
        l_int.append(sorted(t))
    for combi in l_int:
        combi_str = []
        for elt in combi:
            combi_str.append(str(elt))
        l_out.append("|".join(combi_str))
    return l_out


def generation_cands_parCombinaison(dicoCands):
    """
    INPUT = dico: 19: {}, 20: {'avoir;lieu': {'avoir': [2, 3], 'lieu': [4]}}
    OUTPUT_seen = dico avec strings des combinaisons triees par ordre
                  croissant de tokens : le;occasion;être': ['4|13|23'....
    """
    new_dicoCand = {}
    for numPhrase in dicoCands:
        if dicoCands[numPhrase] != {}:
            new_dicoCand[numPhrase] = {}
            for NF in dicoCands[numPhrase]:
                new_dicoCand[numPhrase][NF] = []
                result1 = produit_cartesien(dicoCands[numPhrase][NF])
                result2 = liste_tuples_sorted_list(result1)
                new_dicoCand[numPhrase][NF] = result2
    return new_dicoCand


def annotation_cupt_test(language, chemin_test, chemin_test_annot, localisation_cands_test, NF2categ):
    cands_annotes_LVC_VID = 0
    with open(chemin_test, "r") as test_blind, open(chemin_test_annot, "w") as test_system:  # CHANGEMENT (chemin_test_annot, "a") -> (chemin_test_annot, "w")
        lignes = test_blind.readlines()
        corpus = "".join(lignes[1:])
        test_system.write(str(lignes[0]))
        phrases = corpus.split("\n\n")[:-1]
        for comptPhrase in range(0, len(phrases)):
            lignes = phrases[comptPhrase].split("\n")
            comptMWE = 1
            toks2annot = {}
            toks2categ = {}
            toks2annot_categ = {}
            cand2annot = False
            for cand in localisation_cands_test:
                tokens = cand[1]
                if language not in ["DE", "SV", "ZH"] and len(tokens) > 1:
                    lemmes = []
                    if cand[0] == comptPhrase + 1:
                        toks2categ[comptMWE] = {}
                        for t in cand[1]:
                            if t not in toks2annot:
                                toks2annot[t] = str(comptMWE)
                            else:
                                toks2annot[t] += ";" + str(comptMWE)
                            for l in lignes:
                                infos = l.split("\t")
                                if len(infos) > 2:
                                    if "-" not in str(infos[0]):
                                        if int(infos[0]) == int(t):
                                            if infos[2].lower() in ["me", "te", "nous", "vous"] and language == "FR":
                                                lemme = "se"
                                            elif infos[2].lower() in ["m'", "me", "mi", "vi", "s'", "te", "ti"] and language == "IT":
                                                lemme = "si"
                                            elif "_" in str(infos[2]):
                                                lemme = infos[1].lower()
                                            else:
                                                lemme = infos[2].lower()
                                            lemmes += [lemme]

                        NF = ";".join(sorted(lemmes))
                        NF_lower = []
                        NF_liste = NF.split(";")
                        for elt in NF_liste:
                            NF_lower.append(elt.lower())
                        NF = ";".join(sorted(NF_lower))
                        if NF in NF2categ:
                            cat = NF2categ[NF]
                        else:  # abs car lemmatisation différente
                            cat = "IRV"
                        toks2categ[comptMWE][min(cand[1])] = cat  # attribution de la catégorie au premier token de l'EP
                        for t in cand[1]:
                            if t not in toks2annot_categ:
                                toks2annot_categ[t] = {}
                            toks2annot_categ[t][comptMWE] = cat

                        if "LVC" in str(cat) or "VID" in str(cat):
                            cands_annotes_LVC_VID += 1

                        cand2annot = True
                        comptMWE += 1
                elif language in ["DE", "SV", "ZH"]:
                    lemmes = []
                    if cand[0] == comptPhrase + 1:
                        toks2categ[comptMWE] = {}
                        cand2annot = True
                        for t in cand[1]:
                            if t not in toks2annot:
                                toks2annot[t] = str(comptMWE)
                            else:
                                toks2annot[t] += ";" + str(comptMWE)
                            for l in lignes:
                                infos = l.split("\t")
                                if len(infos) > 2:
                                    if "-" not in str(infos[0]):
                                        if int(infos[0]) == int(t):
                                            if infos[2].lower() in ["me", "te", "nous", "vous"] and language == "FR":
                                                lemme = "se"
                                            elif infos[2].lower() in ["m'", "me", "mi", "vi", "s'", "te", "ti"] and language == "IT":
                                                lemme = "si"
                                            elif "_" in str(infos[2]):
                                                lemme = infos[1].lower()
                                            else:
                                                lemme = infos[2].lower()
                                            lemmes += [lemme]

                        NF = ";".join(sorted(lemmes))
                        NF_lower = []
                        NF_liste = NF.split(";")
                        for elt in NF_liste:
                            NF_lower.append(elt.lower())
                        NF = ";".join(sorted(NF_lower))
                        if NF in NF2categ:
                            cat = NF2categ[NF]
                        else:  # abs car lemmatisation différente
                            cat = "IRV"
                        toks2categ[comptMWE][min(cand[1])] = cat  # attribution de la catégorie au premier token de l'EP
                        for t in cand[1]:
                            if t not in toks2annot_categ:
                                toks2annot_categ[t] = {}
                            toks2annot_categ[t][comptMWE] = cat

                        if "LVC" in str(cat) or "VID" in str(cat):
                            cands_annotes_LVC_VID += 1
                        comptMWE += 1

            if cand2annot:
                # ie au moins un candidat à annoter dans cette phrase
                premiers_toks_annot = []
                for l in lignes:
                    infos = l.split("\t")
                    if "#" in infos[0]:
                        test_system.write(str(l) + "\n")
                    else:
                        if "-" not in infos[0]:
                            if int(infos[0]) in toks2annot:
                                annot = ""
                                comptMWEs = toks2annot[int(infos[0])].split(";")
                                for comptMWE in comptMWEs:
                                    if int(infos[0]) in toks2annot_categ:
                                        if comptMWE not in premiers_toks_annot:
                                            premiers_toks_annot.append(comptMWE)  # car ajoute info catégorie uniquement la 1ere fois
                                            annot += str(comptMWE) + ":" + toks2annot_categ[int(infos[0])][int(comptMWE)] + ";"
                                        else:
                                            annot += str(comptMWE) + ";"
                                annot = annot[:-1]  # suppression dernier ;
                                for i in infos[0:10]:
                                    test_system.write(str(i) + "\t")
                                test_system.write(str(annot) + "\n")
                            else:
                                for i in infos[0:10]:
                                    test_system.write(str(i) + "\t")
                                test_system.write("*\n")
                        else:
                            for i in infos[0:10]:
                                test_system.write(str(i) + "\t")
                            test_system.write("*\n")

            else:
                for l in lignes:
                    infos = l.split("\t")
                    if "#" in infos[0]:
                        test_system.write(str(l) + "\n")
                    else:
                        for i in infos[0:10]:
                            test_system.write(str(i) + "\t")
                        test_system.write("*\n")
            test_system.write("\n")
    return cands_annotes_LVC_VID


def localisation_cands(dicoCands):
    localisation_candidat = []
    for numPhrase in dicoCands:
        for NF in dicoCands[numPhrase]:
            for cand_string in dicoCands[numPhrase][NF]:
                tokensOrdreCroissant = ordonne_iterable(listeStr_2int(cand_string.split("|")))
                localisation_candidat.append((numPhrase, tokensOrdreCroissant))
    return localisation_candidat


def choix_filtres(nb_filtres):
    liste_filtres = []
    for n in range(0, nb_filtres):
        liste_filtres.append([True, False])
    all_configs = []
    for element in itertools.product(*liste_filtres):
        all_configs.append(element)
    dico_config = {}
    for n in range(0, len(all_configs)):
        config = "config_" + str(n)
        dico_config[config] = all_configs[n]
    return dico_config


def eval_TEST(repParent, langue, best_config, numCorpus, nom_filtres, dico_config_filtre, do_eval_test):
    filtres = {}
    for f in range(0, len(nom_filtres)):
        filtres[nom_filtres[f]] = []
        filtres[nom_filtres[f]] = dico_config_filtre["config_" + str(best_config)][f]

    print("meilleure config sur DEV = " + str(filtres))

    if langue == "FR":
        if "faire;il" in NFs:
            NFs.remove("faire;il")  # cf DEV surreprésentation de cette NF qd analyse erreur
    if langue == "RO":
        if "putea;sine" in NFs:
            NFs.remove("putea;sine")  # idem surreprésentation p/p train
    if langue == "GA":
        if "ar;bí" in NFs:
            NFs.remove("ar;bí")  # idem surreprésentation p/p train
        if "bí;ó" in NFs:
            NFs.remove("bí;ó")  # idem surreprésentation p/p train
    cands_allcorpus = NEW_extract_cands(allCorpusPaths, islanguecas, dico_NF2_case_morphoNoun, dico_seqPOS_perCat_POSnorm, NF2POSnormUnique, POSnorm2POSseq, nbMaxInsert, NF2categ, langue, NFs, nbInsertperNF, localisationMWE_train, NF2OrdreVerbes, stats_insertions, pronoms_VID_patron_PRON_PRON_VERB, filtres, dico_ImbricationsMWEs)

    savepickle(cands_allcorpus, str(repOut) + "/cands_allcorpus.pickle")

    # duree_step2= time.time()-tmps_step2
    # print("\n*** Apply best filter on TEST -> DONE in %f" %duree_step2 + " ***")
    # tmps_step3 = time.time()

    # ================================================================
    # annotation TEST cupt
    # ================================================================

    TEST_localisation_candidat = localisation_cands(cands_allcorpus[numCorpus])
    TEST_blind = str(repParent) + "/INPUT/" + str(langue) + "/test.blind.cupt"
    TEST_blind = TEST_blind.replace('"', '')
    TEST_system = str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/test.system_" + str(best_config) + ".cupt"
    cands_annotes_LVC_VID = annotation_cupt_test(langue, TEST_blind, TEST_system, TEST_localisation_candidat, NF2categ)
    copyfile(str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/test.system_" + str(best_config) + ".cupt", str(repParent) + "/RESULT_SYSTEM_SEEN/" + str(langue) + "/test.system.cupt")

    # CHANGEMENT: vérifier l'existance de LANG_nb_seen_annotes_par_sys dans config.cfg avant l'écrire dans le fichier, évider l'erreur quand réutiliser le code
    with open(str(repParent)+'/config.cfg', "r") as f_config:
        text_config = f_config.read()
    lang_count_param = str(langue) + "_nb_seen_annotes_par_sys = "
    if re.search(lang_count_param, text_config):
        new_text_config = re.sub(lang_count_param + r'[0-9]*', lang_count_param + str(cands_annotes_LVC_VID), text_config)
    else:
        new_text_config = text_config + lang_count_param + str(cands_annotes_LVC_VID) + "\n"
    with open(str(repParent)+'/config.cfg', "w") as f_config:
        f_config.write(new_text_config)

    if do_eval_test:
        TEST_gold = str(repParent) + "/INPUT/" + str(langue) + "/test.cupt"
        TRAIN_gold = str(repParent) + "/INPUT/" + str(langue) + "/train.cupt"
        commande = [str(repParent) + "/CODE/evaluate.py", "--gold", TEST_gold, "--pred", TEST_system, "--train", TRAIN_gold]
        chemin_eval_TEST = str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/eval_TEST_config" + str(best_config) + ".txt"
        with open(chemin_eval_TEST, "a") as outfile:
            subprocess.call(commande, stdout=outfile)


def search_best_config_avec_min_filtres_actives(repParent, langue, nb_configs, dico_config_filtre, nb_filtres):
    """
    ## Global evaluation
    * MWE-based: P=232/420=0.5524 R=232/498=0.4659 F=0.5054
    """
    best_F = 0
    best_config = -1
    all_best_configs = {}
    with open(str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/2020_best_configs_Fscore_onDEV.tsv", "a") as f_out, open(str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/2020_configs2Fscore_onDEV.tsv", "a") as f_out2:
        f_out2.write("Configuration de Filtres choisie\tF sur le DEV\n")
        for config in range(0, nb_configs):
            chemin_eval_DEV = str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/DEV/eval_DEV_config" + str(config) + ".txt"
            with open(chemin_eval_DEV, "r") as f:
                lignes = f.readlines()
                F_score = lignes[1].split()[4]
                valeur_F = F_score.split("=")[1]
                f_out2.write("config " + str(config) + "\t" + str(valeur_F) + "\n")
                if float(valeur_F) > best_F:
                    best_F = float(valeur_F)
        for config in range(0, nb_configs):
            chemin_eval_DEV = str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/DEV/eval_DEV_config" + str(config) + ".txt"
            with open(chemin_eval_DEV, "r") as f:
                lignes = f.readlines()
                F_score = lignes[1].split()[4]
                valeur_F = F_score.split("=")[1]
                if float(valeur_F) == best_F:
                    all_best_configs[config] = best_F
        nb_filtres_actives_best = nb_filtres
        for config in all_best_configs:
            nb_filtres_actives = dico_config_filtre["config_" + str(config)].count(True)
            if nb_filtres_actives < nb_filtres_actives_best:
                nb_filtres_actives_best = nb_filtres_actives
                best_config = config
        f_out.write(str(langue) + "\t" + str(best_F) + "\t" + str(config) + "\n")
    return best_config


def search_best_config(repParent, langue, nb_configs):
    """
    ## Global evaluation
    * MWE-based: P=232/420=0.5524 R=232/498=0.4659 F=0.5054
    """
    best_F = 0
    best_config = -1
    # nb_configs = 2**nb_filtres
    with open(str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/2020_best_configs_Fscore_onDEV.tsv", "a") as f_out, open(str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/2020_configs2Fscore_onDEV.tsv", "a") as f_out2:
        f_out2.write("Configuration de Filtres choisie\tF sur le DEV\n")
        for config in range(0, nb_configs):
            chemin_eval_DEV = str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/DEV/eval_DEV_config" + str(config) + ".txt"
            with open(chemin_eval_DEV, "r") as f:
                lignes = f.readlines()
                F_score = lignes[1].split()[4]
                valeur_F = F_score.split("=")[1]
                f_out2.write("config " + str(config) + "\t" + str(valeur_F) + "\n")
                if float(valeur_F) > best_F:
                    best_F = float(valeur_F)
                    best_config = config
        f_out.write(str(langue) + "\t" + str(best_F) + "\t" + str(config) + "\n")
    return best_config


def eval_DEV(repParent, langue, nb_configs):
    for config in range(0, nb_configs):
        DEV_system = str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/DEV/dev.system.config_" + str(config) + ".cupt"
        DEV_gold = str(repParent) + "/INPUT/" + str(langue) + "/dev.cupt"
        TRAIN_gold = str(repParent) + "/INPUT/" + str(langue) + "/train.cupt"
        commande = [str(repParent) + "/CODE/evaluate.py", "--gold", DEV_gold, "--pred", DEV_system, "--train", TRAIN_gold]
        chemin_eval_DEV = str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/DEV/eval_DEV_config" + str(config) + ".txt"
        if not os.path.exists(chemin_eval_DEV):
            with open(chemin_eval_DEV, "a") as outfile:
                subprocess.call(commande, stdout=outfile)


# ===============================================
#       &&    MAIN  &&
# ===============================================
tmps_step0 = time.time()
repParent = "/".join(os.path.abspath(os.path.dirname(sys.argv[0])).split("/")[:-1])
# ------------------------------------------
# Parameters to put into configFile :
do_extract_cands = True
# ------------------------------------------
# Parameters already in configFile :
config = configparser.ConfigParser()
config.read(str(repParent) + '/config.cfg')
corpusTRAIN = config.get('Parameters', 'corpusTRAIN')
corpusDEV = config.get('Parameters', 'corpusDEV')
corpusTEST = config.get('Parameters', 'corpusTEST')
languesAtraiter = ast.literal_eval(config.get('Parameters', 'langues'))
choix_topX_POSnorm = int(config.get('Parameters', 'topX_POSnorm'))
debug = config.get('Parameters', 'debug')
allCorpusPaths, colonnesPOS = obtentionCheminCorpus(languesAtraiter)
do_eval_test = config.get('Parameters', 'calculPerfoTEST')
annotation_ONLY = ast.literal_eval(config.get('Parameters', 'annotation_ONLY'))  # CHANGEMENT :  ajout paramètre, c'est un booléen
best_configALL = ast.literal_eval(config.get('Parameters', 'best_configALL'))  # CHANGEMENT :  ajout paramètre, c'est un dictionnaire
# ==============================================================
# STEP 1: Caractéristiques des MWE annotées dans TRAIN
# ==============================================================
NF2POSseq = {}
POSnorm2POSseq = {}
NF2categ = {}
NF2flexion = {}
NF2POSandLemme = {}
NF2POSnorm_details = {}
NF2POSnorm = {}
topX_POSnorm = {}
dicoMorpho = {}
listePOS = {}
listeRelDep = {}
nbMaxInsert = {}
localisationMWE = {}
dicoNumPhrase2Idphrase = {}
dicoFreqNF_inTrain = {}
# ===============================================
message = "All languages-MWE extract infos"
pbar = tqdm(languesAtraiter, desc=message)
for langue in pbar:
    repOut = str(repParent) + "/OUTPUT_seen/INFOS/" + str(langue)
    if not os.path.exists(str(repOut) + "/localisationMWE_train.pickle"):
        os.makedirs(repOut)
        dicoMorpho, listePOS, listeRelDep = cupt2POSdepMorpho(langue, allCorpusPaths[langue], colonnesPOS[langue])
        NF2OrdreVerbes, dico_NF2_case_morphoNoun, pronoms_VID_patron_PRON_PRON_VERB, NF2OrdreVerbes, stats_insertions, dico_ImbricationsMWEs, dico_seqPOS_perCat_POSnorm = NEW_infosSup_Train(langue, allCorpusPaths[langue], colonnesPOS[langue], debug, dicoMorpho, listePOS, listeRelDep)
        localisationMWE_train, NF2POSseq, POSnorm2POSseq, NF2categ, NF2flexion, NF2POSnormUnique, topX_POSnorm, nbMaxInsert, dicoNumPhrase2Idphrase, dicoFreqNF_inTrain, nbInsertperNF = infos_Train2(langue, allCorpusPaths[langue], colonnesPOS[langue], choix_topX_POSnorm, debug, dicoMorpho, listePOS, listeRelDep)
        savepickle(localisationMWE_train, str(repOut) + "/localisationMWE_train.pickle")
        savepickle(NF2POSseq, str(repOut) + "/NF2POSseq.pickle")
        savepickle(POSnorm2POSseq, str(repOut) + "/POSnorm2POSseq.pickle")
        savepickle(NF2categ, str(repOut) + "/NF2categ.pickle")
        savepickle(NF2flexion, str(repOut) + "/NF2flexion.pickle")
        savepickle(NF2POSnormUnique, str(repOut) + "/NF2POSnormUnique.pickle")
        savepickle(nbMaxInsert, str(repOut) + "/nbMaxInsert.pickle")         # Nb max d'insertions par catégorie en conservant hapax
        savepickle(dicoNumPhrase2Idphrase, str(repOut) + "/dicoNumPhrase2Idphrase.pickle")
        savepickle(dicoFreqNF_inTrain, str(repOut) + "/dicoFreqNF_inTrain.pickle")
        savepickle(nbInsertperNF, str(repOut) + "/nbInsertperNF.pickle")
        savepickle(pronoms_VID_patron_PRON_PRON_VERB, str(repOut) + "/pronoms_VID_patron_PRON_PRON_VERB.pickle")
        savepickle(stats_insertions, str(repOut) + "/stats_insertions.pickle")  # Nb max d'insertions par catégorie HORS hapax
        savepickle(NF2OrdreVerbes, str(repOut) + "/NF2OrdreVerbes.pickle")
        savepickle(dico_ImbricationsMWEs, str(repOut) + "/dico_ImbricationsMWEs.pickle")
        savepickle(dico_seqPOS_perCat_POSnorm, str(repOut) + "/dico_seqPOS_perCat_POSnorm.pickle")
        savepickle(dico_NF2_case_morphoNoun, str(repOut) + "/dico_NF2_case_morphoNoun.pickle")
    else:
        localisationMWE_train = loadpickle(str(repOut) + "/localisationMWE_train.pickle")
        NF2POSseq = loadpickle(str(repOut) + "/NF2POSseq.pickle")
        POSnorm2POSseq = loadpickle(str(repOut) + "/POSnorm2POSseq.pickle")
        NF2categ = loadpickle(str(repOut) + "/NF2categ.pickle")
        NF2flexion = loadpickle(str(repOut) + "/NF2flexion.pickle")
        NF2POSnormUnique = loadpickle(str(repOut) + "/NF2POSnormUnique.pickle")
        nbMaxInsert = loadpickle(str(repOut) + "/nbMaxInsert.pickle")
        dicoNumPhrase2Idphrase = loadpickle(str(repOut) + "/dicoNumPhrase2Idphrase.pickle")
        dicoFreqNF_inTrain = loadpickle(str(repOut) + "/dicoFreqNF_inTrain.pickle")
        nbInsertperNF = loadpickle(str(repOut) + "/nbInsertperNF.pickle")
        pronoms_VID_patron_PRON_PRON_VERB = loadpickle(str(repOut) + "/pronoms_VID_patron_PRON_PRON_VERB.pickle")
        stats_insertions = loadpickle(str(repOut) + "/stats_insertions.pickle")
        NF2OrdreVerbes = loadpickle(str(repOut) + "/NF2OrdreVerbes.pickle")
        dico_ImbricationsMWEs = loadpickle(str(repOut) + "/dico_ImbricationsMWEs.pickle")
        dico_seqPOS_perCat_POSnorm = loadpickle(str(repOut) + "/dico_seqPOS_perCat_POSnorm.pickle")
        dico_NF2_case_morphoNoun = loadpickle(str(repOut) + "/dico_NF2_case_morphoNoun.pickle")
    NFs = list(NF2POSnormUnique.keys())

    # ===================================================================
    # STEP 2 : Extract candidates in TRAIN, (DEV) and TEST
    # ===================================================================
    # ======================================================================================
    #                   optimisation sur DEV
    # ======================================================================================
    nom_filtres = ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8"]
    nb_filtres = len(nom_filtres)
    dico_config_filtre = {}
    dico_config_filtre = choix_filtres(nb_filtres)  # nbconfigs =  2^nbfiltres
    nb_configs = 2**nb_filtres
    # ==============================================================================================
    islanguecas = verif_languecas(dico_NF2_case_morphoNoun)
    if annotation_ONLY:  # CHANGEMENT : ajout condition
        best_config = best_configALL[langue]
        filtres = {}
        liste_traits_actives_VraiFaux = dico_config_filtre[f"config_{best_config}"]
        for f in range(0, nb_filtres):
            filtres[nom_filtres[f]] = liste_traits_actives_VraiFaux[f]
        print(f"Configuration {langue}{best_config}: {filtres}")
        thisCorpusPath = {}
        if len(sys.argv) > 1:
            nomCorpus = sys.argv[1].split('/')[-1]
            pathCORPUS = str(repParent) + "/INPUT/" + str(langue) + "/" + nomCorpus  # Au cas où ils précisent le chemin
            thisCorpusPath[langue] = []  # CHANGEMENT
            for fichier in glob.glob(f"{pathCORPUS}/*.txt"):  # TODO: no need? thisCorpusPath is for ?
                corpus_uri = "http://my/newcorpus/uri"
                file_txt2cupt(fichier, f"{fichier.split('.txt')[0]}.cupt", corpus_uri)
            for fichier in glob.glob(f"{pathCORPUS}/*.cupt"):
                thisCorpusPath[langue].append(fichier)
        else:
            print("ERREUR")
            print("Vous êtes en mode annotation_ONLY : "
                  "changez de configuration ou entrez un corpus en argument.")
            print(f"Le corpus doit être un répertoire et se trouver"
                  f" dans Seen2Seen/INPUT/{langue}.")
            sys.exit()
        cands_allcorpus = NEW_extract_cands(thisCorpusPath, islanguecas, dico_NF2_case_morphoNoun, dico_seqPOS_perCat_POSnorm, NF2POSnormUnique, POSnorm2POSseq, nbMaxInsert, NF2categ, langue, NFs, nbInsertperNF, localisationMWE_train, NF2OrdreVerbes, stats_insertions, pronoms_VID_patron_PRON_PRON_VERB, filtres, dico_ImbricationsMWEs)
        dico_traitMWETEST_perNF = {}
        message = str(langue) + ":" + "Annotation"
        pbar = tqdm(range(0, len(thisCorpusPath[langue])), desc=message)
        for corpus in pbar:
            nomFichier = thisCorpusPath[langue][corpus].split('/')[-1]
            dicoPhrases = cupt2phrases(thisCorpusPath[langue][corpus])
            dev_localisation_candidat = NEW_localise_cands(dicoPhrases, cands_allcorpus[corpus])
            pathIN = str(repParent) + "/INPUT/" + str(langue) + "/" + str(nomCorpus) + "/" + str(nomFichier)
            chemin_dev_annot = str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/ANNOT/" + str(nomCorpus) + "/" + str(nomFichier).split('.cupt')[0] + "annote.config" + str(best_config) + ".cupt"
            rep_dev_annot = str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/ANNOT/" + str(nomCorpus) + "/"
            if not os.path.exists(rep_dev_annot):
                os.makedirs(rep_dev_annot)
            annotation_cupt_test(langue, pathIN, chemin_dev_annot, dev_localisation_candidat, NF2categ)
    else:
        # TRAIN ET DEV
        """with open("liste_langue_cas.tsv", "a") as f_out:
            f_out.write(str(langue) + "\tLangue cas = " + str(islanguecas) + "\n")"""
        if not os.path.exists(str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/DEV"):
            os.makedirs(str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/DEV")
            message = str(langue) + ":" + "search best filter combination"
            pbar = tqdm(dico_config_filtre, desc=message)
            for config in pbar:
                filtres = {}
                liste_traits_actives_VraiFaux = dico_config_filtre[config]
                for f in range(0, len(nom_filtres)):
                    filtres[nom_filtres[f]] = liste_traits_actives_VraiFaux[f]
                with open("infos_configs.tsv", "a") as f_out:
                    f_out.write(str(config) + "\t" + str(liste_traits_actives_VraiFaux) + "\n")
                cands_allcorpus = NEW_extract_cands(allCorpusPaths, islanguecas, dico_NF2_case_morphoNoun, dico_seqPOS_perCat_POSnorm, NF2POSnormUnique, POSnorm2POSseq, nbMaxInsert, NF2categ, langue, NFs, nbInsertperNF, localisationMWE_train, NF2OrdreVerbes, stats_insertions, pronoms_VID_patron_PRON_PRON_VERB, filtres, dico_ImbricationsMWEs)
                dico_traitMWETEST_perNF = {}
                corpus = 1
                dicoPhrases = cupt2phrases(allCorpusPaths[langue][corpus])
                dev_localisation_candidat = NEW_localise_cands(dicoPhrases, cands_allcorpus[corpus])
                pathDEV = str(repParent) + "/INPUT/" + str(langue) + "/" + str(corpusDEV)
                pathDEV = pathDEV.replace('"', '')
                chemin_dev_annot = str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/DEV/dev.system." + str(config) + ".cupt"
                annotation_cupt_test(langue, pathDEV, chemin_dev_annot, dev_localisation_candidat, NF2categ)
        chemin_eval_DEV = str(repParent) + "/OUTPUT_seen/EVAL_allLanguages/" + str(langue) + "/DEV/eval_DEV_config" + str(config) + ".txt"
        if not os.path.exists(chemin_eval_DEV):
            eval_DEV(repParent, langue, nb_configs)                 # script evaluation du DEV => F-mesure pour toutes les configs
        best_config = search_best_config_avec_min_filtres_actives(repParent, langue, nb_configs, dico_config_filtre, nb_filtres)

        # CHANGEMENT: rajouter la meilleure config trouvée dans le fichier config
        best_configALL[langue] = best_config
        with open(str(repParent) + '/config.cfg', "r") as f_config:
            text_config = f_config.read()
        new_text_config = re.sub(r'best_configALL = \{.*\}', f'best_configALL = {str(best_configALL)}', text_config)
        with open(str(repParent) + '/config.cfg', "w") as f_config:
            f_config.write(new_text_config)

        # ======================================================================================
        #                     annotation TEST
        # ======================================================================================
        if not os.path.exists(str(repParent) + "/RESULT_SYSTEM_SEEN/"):
            os.makedirs(str(repParent) + "/RESULT_SYSTEM_SEEN/")
        if os.path.exists(str(repParent) + "/INPUT/" + str(langue) + "/test.blind.cupt"):
            if not os.path.exists(str(repParent) + "/RESULT_SYSTEM_SEEN/" + str(langue)):
                os.makedirs(str(repParent) + "/RESULT_SYSTEM_SEEN/" + str(langue))
            eval_TEST(repParent, langue, best_config, 2, nom_filtres, dico_config_filtre, do_eval_test)
