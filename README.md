# MWE_coref

Ce repository sert à collecter les travaux faits pour étudier les expressions polylexicales et la coréférence.

## Sujet

Ce repository a été créé dans le cadre d'un stage dont l'objectif est de vérifer de manière expérimentale l'hypothèse selon laquelle les composants individuels d'une expression polylexicale sont rarement susceptibles d'appartenir à des chaînes de coréférences.

**Expressions polylexicales** : Termes complexes composés de plusieurs mots tels que "blanc d'œuf", "mémoire vive", "prendre une pause", "prendre le temps", "tourner sa veste" ou "prendre le taureau par les cornes" etc. Elles présentent des comportements linguistiques irréguliers et notamment la non-compositionnalité sémantique, qui signifie que le sens global de l'expression n'est pas déductible de manière régulière à partir des sens des composants et des liens syntaxiques qui les relient.
**Chaînes de coréférence** : Procédé linguistique dans lequel plusieurs
éléments d'un discours réfèrent à un même élément du discours.

Exemple : "Il a retourné sa veste et l'a suspendue dans l'armoire."
Ici le groupe nominal _la veste_ est ce que l'on appelle une **mention**,
c'est à dire un élément qui réfère d'une entité du monde du discours
(la veste qui appartient à la personne décrite dans l'énoncé). De même,
le pronom _l'_ est lui-même une mention qui réfère à cette même entité
du discours. On dit alors que _sa veste_ et _l'_ sont coréférents,
c'est-à-dire qu'ils désignent la même entité.

Pour vérifier cette hypothèse, nous avons à disposition un outil qui nous permet de 

## Pré-requis

Installation OFCORS/Seen2seen

## Structure du repository

```
|-- MWE_coref
    |-- .gitignore
    |-- README.md
    |-- seen2seen
    |   |-- udpipe_annote.py
    |-- SEQUOIA
    |   |-- EMEA_cupt
    |   |-- EMEA_txt
    |   |-- frwiki_cupt
    |   |-- frwiki_txt
    |   |-- z_fichier_intermediaire
    |   |-- get_text_brut.py
    |   |-- corpus_split2text.py
    |   |-- couper_emea.py
    |   |-- get_MWE_from_cupt.py
    |   |-- mwe_all.py
    |   |-- MWE_decompte_*.json
    |   |-- ...
    |-- OFCORS
        |-- CuptParser.py
        |-- OfcorsFilesParser.py
        |-- merge_s2s_ofcors.py
        |-- statistiques.py
        |-- lanceur.sh
        |-- blabla
        |-- phrases
        |-- SEQUOIA_EMEA
        |-- SEQUOIA_frwiki
        |-- z_oldies
             ...
```

## Processus de travail

1. Modification du script de Seen2seen, pour qu'il puisse faire seulement l'étape d'annotation;

    - Script `udpipe_annote.py` pour transformer un fichier txt en `cupt.blind`;
    - Modification du script `seen2seen.py` en créant un mode "annotation_ONLY" qui permet de ne faire que l'annotation sans refaire l'entraînement. Ce mode est à spécifier dans le fichier de config (`config.cfg`) avec "annotation_ONLY = True".


2. Utilisation du corpus SEQUOIA dans PARSEME, séparation des sous-corpus EMEA et frwiki selon les articles;

    - Lien pour télécharger le [corpus](https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3429)
    - Sélection manuelle des parties "emea" et "frwiki" dans le fichier `sequoia-ud.conllu` (puisqu'il est ordonné) pour créer deux fichiers `emea.conllu` et `frwiki.conllu`, utilisation du script `get_text_brut.py` pour extraire d'abord le texte brut et leurs sent_id dans fichiers `emea_textbrut.txt` et `frwiki_textbrut.txt`
    - Division manuelle du corpus en articles, avec l'annotation "## DEBUT DOC" et "## FIN DOC" dans `emea_textbrut.txt` et `frwiki_textbrut.txt`
    - À partir du contenu du fichier cupt, utilisation de `corpus_split2text.py` pour former le fichier `cupt` et `txt` de chaque article selon le sent_id choisi et le source_sent_id dans le fichier cupt (téléchargement de cupt de [PARSEME](https://gitlab.com/parseme/parseme_corpus_fr)), un article par fichier
    - Répertoire du corpus obtenu: `./OFCORS/SEQUOIA_EMEA` et `./OFCORS/SEQUOIA_frwiki`, ou `*_cupt` et `*_txt` dans `SEQUOIA`

3. Fusion du résultat de OFCORS et de celui de Seen2seen au format cupt : ajout de 2 colonnes : la colonne des mentions et celle des chaînes de coréférences;

    - Format : colonne des mentions : id de mentions séparés par `;`
               colonnes des coréférences : `id_de_chaînes:id_de_mention`, séparés par `;`Exemple :

        ```
        ...
        6	ses	son	DET	_	Gender=Masc|Number=Plur|Poss=Yes|PronType=Prs	7	det	_	_	*	5;6	7:5;7:6
        7	parents	parent	NOUN	_	Gender=Masc|Number=Plur	2	obl:mod	_	_	*	5;6	7:5;7:6
        8	et	et	CCONJ	_	_	11	cc	_	_	*	6	7:6
        9	sa	son	DET	_	Gender=Fem|Number=Sing|Poss=Yes|PronType=Prs	11	det	_	_	*	6;7	7:6
        10	petite	petit	ADJ	_	Gender=Fem|Number=Sing	11	amod	_	_	*	6;7	7:6
        11	sœur	sœur	NOUN	_	Gender=Fem|Number=Sing	7	conj	_	_	*	6;7	7:6
        ...
        ```

    - Scripts pour les fusionner : `CuptParser.py`, `OfcorsFilesParser.py` et `merge_s2s_ofcors.py`
    - Script pour lancer tout :`lanceur.sh`
    - Script pour étudier le résultat :  `statistiques.py`
    - Répertoires de test : `blabla`, `phrases`, `SEQUOIA_EMEA`, `SEQUOIA_frwiki`
    - Anciens scripts : `z_oldies`

# UTILISATION : Partie OFCORS

## Exemples de lancement:


    ./lanceur.sh -os blabla/
    
Cette commande lance tout le processus sur les fichiers contenus dans le répertoire `blabla/`. Ce répertoire doit contenir les fichiers textes et les fichiers cupt annotés en MWEs (passés dans Seen2seen) du corpus.
Les fichiers textes sont d'abord passés dans OFCORS et les fichiers résultats (`{nom}_resulting_chains.json`, `{nom}_mentions_output.json` et `{nom}_token.json`) sont créés dans `blabla/ofcors_outputs`. Ensuite, le script `merge_s2s_ofcors.py` est appelé pour créer les fichiers cupt avec les deux colonnes supplémentaires dans le dossier `blabla/mwecoref_outputs` à partir des sorties d'OFCORS et des fichiers cupt. Enfin, le script `statistiques.py` affiche les résultats dans le terminal.


    ./lanceur.sh -o blabla/


Cette commande ne lance que la partie OFCORS.


    ./lanceur.sh -s blabla/


Cette commande ne lance que les scripts `merge_s2s_ofcors.py` et `statistiques.py`. Elle nécessite que les fichiers résultats de OFCORS se trouvent dans `blabla/mwecoref_outputs`.

# UTILISATION : Partie Seen2seen

## Lancement ...

# RÉSULTATS

## Expliquer stats ...