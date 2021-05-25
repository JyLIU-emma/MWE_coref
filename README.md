# MWE_coref

Un repository sert à collecter les travaux faits pour étudier les expressions polylexicales et les coréférences.

## Structure du repository

```
|-- MWE_coref
    |-- .gitignore
    |-- README.md
    |-- seen2seen
    |   |-- udpipe_annote.py
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

1. Modifier le script de seen2seen, pour qu'il puisse faire seulement l'étape d'annotation;

    - script `udpipe_annote.py` pour transformer un fichier txt en `cupt.blind`;
    - modifier le script `seen2seen.py` (**à compléter**)


2. Utiliser le corpus SEQUOIA dans PARSEME, séparer ses sous-corpus EMEA et frwiki par les articles;

    - lien pour télécharger le [corpus](https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3429)
    - sélectionner manuellement les parties "emea" et "frwiki" dans le fichier `sequoia-ud.conllu` (puisqu'il est ordonné) pour créer deux fichiers `emea.conllu` et `frwiki.conllu`, utiliser script "get_text_brut.py" pour extraître d'abord le texte brut et leurs sent_id dans fichiers `emea_textbrut.txt` et `frwiki_textbrut.txt`
    - diviser manuellement le corpus en article, avec l'annotation "## DEBUT DOC" et "## FIN DOC" dans `emea_textbrut.txt` et `frwiki_textbrut.txt`
    - À partir du contenu dans cupt, former le fichier `cupt` et `txt` de chaque article selon le sent_id choisi et le source_sent_id dans cupt (téléchargement de cupt de [PARSEME](https://gitlab.com/parseme/parseme_corpus_fr)), un article par fichier
    - répertoire de corpus obtenu: `./OFCORS/SEQUOIA_EMEA` et `./OFCORS/SEQUOIA_frwiki`

3. Fusionner le résultat de l'OFCORS au format cupt : ajout de 2 colonnes : colonne des mentions et colonne des coréférences;

    - format : colonne des mentions : id de mentions séparés par `;` ; colonnes des coréférences : `id_de_chaînes:id_de_mention`, séparés par `;`, exemple :

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

    - script pour les fusionner : `CuptParser.py`, `OfcorsFilesParser.py` et `merge_s2s_ofcors.py`
    - script pour lancer tout :`lanceur.sh`
    - script pour étudier le résultat :  `statistiques.py`
    - répertoire de test : `blabla`, `phrases`, `SEQUOIA_EMEA`, `SEQUOIA_frwiki`
    - anciens script : `z_oldies`