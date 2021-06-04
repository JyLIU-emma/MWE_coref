# MWE_coref

Ce repository sert à collecter les travaux réalisés pour étudier les expressions polylexicales et la coréférence.

## Sujet

Ce repository a été créé dans le cadre d'un stage dont l'objectif est de vérifer de manière expérimentale l'hypothèse selon laquelle les composants individuels d'une expression polylexicale sont rarement susceptibles d'appartenir à des chaînes de coréférences.

**Expressions polylexicales** : Termes complexes composés de plusieurs mots tels que "blanc d'œuf", "mémoire vive", "prendre une pause", "prendre le temps", "retourner sa veste" ou "prendre le taureau par les cornes" etc. Elles présentent des comportements linguistiques irréguliers et notamment la non-compositionnalité sémantique, qui signifie que le sens global de l'expression n'est pas déductible de manière régulière à partir des sens des composants et des liens syntaxiques qui les relient.  
**Chaînes de coréférence** : Procédé linguistique dans lequel plusieurs éléments d'un discours réfèrent à un même élément du discours.

Exemple : "Il a retourné sa veste et l'a suspendue dans l'armoire."   Ici le groupe nominal _la veste_ est ce que l'on appelle une **mention**, c'est-à-dire un élément qui réfère d'une entité du monde du discours (la veste qui appartient à la personne décrite dans l'énoncé). De même, le pronom _l'_ est lui-même une mention qui réfère à cette même entité du discours. On dit alors que _sa veste_ et _l'_ sont **coréférents**, c'est-à-dire qu'ils désignent la même entité.

Dans l'exemple précédent, la coréférence entre le pronom et _sa veste_ n'est possible que parce que nous ne sommes pas en présence de l'expression polylexicale "retourner sa veste" ("changer d'opinion"). Si la phrase "Il a retourné sa veste" avait été une EP, la non-compositionnalité de celle-ci aurait empêché de rendre le composant _sa veste_ accessible à une coréférence. C'est ce type de restriction que nous souhaitons étudier au cours de ce stage.

Pour vérifier cette hypothèse, nous avons à disposition un outil pour l'annotation en expressions polylexicales ([Seen2seen](https://gitlab.com/cpasquer/st_2020)) et un outil pour la résolution de coréférences ([OFCORS](https://gitlab.com/Stanoy/ofcors/-/tree/master), qui utilise [DECOFRE](https://github.com/LoicGrobol/decofre) pour la reconnaissance de mentions). Les entrées et les sorties diffèrent d'un outil à l'autre.

## Installation des outils

Pour pouvoir utiliser notre repository, il faut installer Seen2seen et OFCORS. Il est conseillé d'utiliser un environnement virtuel.

### Installation de Seen2seen
Pour plus de détails, référez-vous au README de Seen2seen : [Lien vers Seen2seen](https://gitlab.com/cpasquer/st_2020).
* Clonez le repository de Seen2seen: `git clone https://gitlab.com/cpasquer/st_2020 Seen2Seen`
* Clonez ce repository : `git clone https://github.com/anaelle-p/MWE_coref`
* Supprimez l'ancien code et l'ancien fichier config : `rm Seen2Seen/CODE/seen2seen.py Seen2Seen/config.cfg`
* Copiez-collez le nouveau code : `cp MWE_coref/seen2seen/seen2seen.py Seen2Seen/CODE/seen2seen.py`
* Copiez-collez le nouveau fichier config : `cp MWE_coref/seen2seen/config.cfg Seen2Seen/config.cfg`
* Ajoutez le script de conversion udpipe : `cp MWE_coref/seen2seen/udpipe_annote.py Seen2Seen/CODE/udpipe_annote.py`
* Ajoutez le modèle utilisé par le script de conversion : `cp -r MWE_coref/seen2seen/model_udpipe Seen2Seen/CODE/model_udpipe/`  
Vous pouvez maintenant utiliser Seen2seen pour l'annotation ! Le lancement est expliqué plus bas.

### Installation d'OFCORS
Pour plus de détails, référez-vous au README d'OFCORS : [Lien vers OFCORS](https://gitlab.com/Stanoy/ofcors/-/tree/master).
* Clonez le repository d'OFCORS : `git clone https://gitlab.com/Stanoy/ofcors.git`
* Installez flit si besoin : `pip install flit`
* Rendez-vous dans le répertoire ofcors : `cd ofcors`
* `flit build --format wheel`
* `pip install dist/ofcors-X.Y.Z-py3-none-any.whl`  
Ofcors est installé!
* Téléchargez les modèles d'OFCORS : [models.zip](https://gitlab.com/Stanoy/ofcors/-/releases/v0.4.4)
* Déplacez le dossier `models` dans `ofcors/models`
* N'oubliez pas d'installer les modèles de Spacy (`python -m spacy download fr_core_news_lg`) et de Stanza (`python3`, `import stanza`, `stanza.download('fr')`)
* Lancez ofcors sur une phrase : `ofcors-infer "Ainsi, Pierre a le privilège d'admirer chaque jour l'un des monuments les plus visités au monde !"`
* Sortez d'Ofcors : `cd ..`
* Si vous n'avez pas cloné notre repository : `git clone https://github.com/anaelle-p/MWE_coref`
* Récupérez les fichiers dont OFCORS a besoin : `cp -r ofcors/ofcors_outputs/ MWE_coref/OFCORS/ofcors_outputs`  
Vous pouvez maintenant utiliser OFCORS dans notre repository! Le lancement est expliqué plus bas.

## Choix de corpus

Pour traiter correctement la coréférence, il est nécessaire de connaître les frontières de textes dans un corpus. En effet, la coréférence ne peut être traitée qu'à l'intérieur d'une même unité discursive.  
Le [corpus PARSEME](https://gitlab.com/parseme/parseme_corpus_fr) est annoté en expressions polylexicales mais les frontières des textes ne sont pas annotées. Ce corpus contient quatre sous-corpus (SEQUOIA, GSD, PARTUT et PUD) et il n'est possible de retrouver l'ordre des phrases que pour un seul sous-corpus : [SEQUOIA](https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3429).  
Nous avons donc isolé les différents documents présents dans le corpus SEQUOIA :
* 2 documents de l'agence européenne du médicament pour la partie EMEA (\~ 1000 phrases en tout)
* 19 pages Wikipédia pour la partie frwiki (\~ 1000 phrases en tout)

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
    - Sélection manuelle des parties "emea" et "frwiki" dans le fichier `sequoia-ud.conllu` (puisqu'il est ordonné) pour créer deux fichiers `emea.conllu` et `frwiki.conllu`, utilisation du script `get_text_brut.py` pour extraire d'abord le texte brut et leurs sent_id dans fichiers `emea_textbrut.txt` et `frwiki_textbrut.txt`
    - Division manuelle du corpus en articles, avec l'annotation "## DEBUT DOC" et "## FIN DOC" dans `emea_textbrut.txt` et `frwiki_textbrut.txt`
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
    - Script pour étudier le résultat :  `statistiques.py`
    - Répertoires de test : `blabla`, `phrases`, `SEQUOIA_EMEA`, `SEQUOIA_frwiki`
    - Anciens scripts : `z_oldies`

## Utilisation

### Lancement de Seen2seen en version Train et Test
Si vous n'avez jamais lancé Seen2seen vous pouvez commencer par lancer l'entrainement et le test. Attention, c'est assez long.  
Vous aurez besoin du fichier `test.cupt`. Si vous ne l'avez pas, téléchargez-le [ici](https://gitlab.com/parseme/sharedtask-data/-/tree/master/1.2/) et déplacez-le dans le répertoire `Seen2Seen/INPUT/FR/`.  
Le mode annotation_ONLY doit être désactivé (`annotation_ONLY = False` ligne 13 du fichier `Seen2Seen/config.cfg`)  
Vous devez vous trouver dans `Seen2Seen/CODE/`.  

    python3 seen2seen.py

À la fin du traitement, la meilleure configuration de filtres pour le français est mise à jour automatiquement dans le fichier `Seen2Seen/config.cfg`.

### Lancement de Seen2seen en version annotation_ONLY
Le répertoire du corpus à analyser doit se trouver dans `Seen2seen/INPUT/FR/`.  
Les fichiers du corpus sont donc dans `Seen2seen/INPUT/FR/{nom_repertoire_corpus}/`  
Ils doivent être soit au format .cupt soit au format .txt.  
Le mode annotation_ONLY doit être activé (`annotation_ONLY = True` ligne 13 du fichier `Seen2Seen/config.cfg`)  
Vous devez vous trouver dans `Seen2Seen/CODE/`.  

    python3 seen2seen.py {nom_repertoire_corpus}

OU

    python3 seen2seen.py Seen2seen/INPUT/FR/{nom_repertoire_corpus}/

Dans les deux cas seul le nom du répertoire sera pris en compte.
Les résultats de l'annotation se trouvent dans `Seen2Seen/OUTPUT_seen/ANNOTATIONS/FR/{nom_repertoire_corpus}/` et se terminent par`_annote.config48.cupt`.

### Lancement d'OFCORS et de la fusion:
Vous devez vous trouvez dans `MWE_coref/OFCORS/`.  

    ./lanceur.sh -os blabla/
    
Cette commande lance tout le processus sur les fichiers contenus dans le répertoire `blabla/`. Ce répertoire doit contenir les fichiers textes et les fichiers cupt annotés en MWEs (passés dans Seen2seen) du corpus.
Les fichiers textes sont d'abord passés dans OFCORS et les fichiers résultats (`{nom}_resulting_chains.json`, `{nom}_mentions_output.json` et `{nom}_token.json`) sont créés dans `blabla/ofcors_outputs`. Ensuite, le script `merge_s2s_ofcors.py` est appelé pour créer les fichiers cupt avec les deux colonnes supplémentaires dans le dossier `blabla/mwecoref_outputs` à partir des sorties d'OFCORS et des fichiers cupt. Enfin, le script `statistiques.py` affiche les résultats dans le terminal.


    ./lanceur.sh -o blabla/


Cette commande ne lance que la partie OFCORS.


    ./lanceur.sh -s blabla/


Cette commande ne lance que les scripts `merge_s2s_ofcors.py` et `statistiques.py`. Elle nécessite que les fichiers résultats de OFCORS sur les fichiers de `blabla/` se trouvent dans `blabla/ofcors_outputs`.

## Résultats
```
    FICHIER : frwiki_7_mwe_coref.cupt
    PHRASE : L'instruction a révélé l'existence d'une lettre datée de décembre 1993 et signée par Jacques Chirac, qui demande à son administration d'accorder une promotion à une employée municipale, Madeleine Farrad, qui, bien que rémunérée par la ville, travaille en fait au siège du RPR.
    INFOS : tokens : ['accorder', 'promotion'], coref : ['*', '13:69'], cas : {'69': 4}
    CHAÎNE(S) : 
       - 13 : {'69': ['une', 'promotion'], '70': ['une', 'employée', 'municipale'], '72': ['Madeleine', 'Farrad', ',']}

```
Les différentes expressions polylexicales faisant parties d'une chaîne de coréférence sont regroupées par type (VID, LVC.full ...). Pour chaque type sont ensuite affichées les informations sur les expressions polylexicales comme ci-dessus.
* FICHIER :  le fichier où se trouve l'EP.
* PHRASE :  La phrase où se trouve l' EP.
* INFOS : 
    - Les tokens qui composent l'EP.
    - Pour chaque token : son appartenance ou non à une chaîne de coréférence. Si `*` alors il n'appartient pas à une chaîne, sinon `indice de chaine : indice de mention`. Dans l'exemple ci-dessus, "promotion" correspond à la mention 69 et fait partie de la chaîne de coréférence 13.
    - Le cas correspondant pour chaque mention. (CAS 1 : la mention déborde de l'EP, CAS 2 : la mention et l'EP sont identiques, CAS 3 : la mention correspond à un élément de l'EP et CAS 4 : MWE = accorder(1) une(\*) promotion(1)/MENTION = accorder(\*) une(1) promotion(1))
* CHAINE(S) : Pour chaque chaîne à laquelle l'EP appartient, on affiche l'ensemble des mentions de la chaîne. Dans l'exemple ci-dessus une seule chaîne a été trouvée, on affiche donc uniquement la chaîne 13 qui contient les mentions 69 ("une promotion"), 70 ("une employée municipale") et 72 ("Madeleine Farrad").

_Les résultats ne sont pas encore parfaits. La chaîne de coréférence présentée ici n'est pas correcte et ne sert que d'exemple pour les explications._