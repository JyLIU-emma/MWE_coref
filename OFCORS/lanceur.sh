#!/bin/bash

# ./lanceur.sh phrases/ -os
# Dans phrases/ se trouve les fichiers txt à analyser par OFCORS
# La sortie d'OFCORS se trouve dans phrases/ofcors_outputs/

ofcors()
{
    for fichier in `ls $1*.txt`
        do
            echo "--------------------------------------"
            echo $fichier
            ofcors-infer -f -p window $fichier

            new_fichier=(${fichier//\// })
            new_fichier=(${new_fichier[1]//./ })
            echo ${new_fichier[0]}

            mv ./ofcors_outputs/resulting_chains.json ./$1ofcors_outputs/${new_fichier[0]}_resulting_chains.json
            mv ./ofcors_outputs/mentions_detection/mentions_output.json ./$1ofcors_outputs/${new_fichier[0]}_mentions_output.json
        done
}

mwecoref()
{
    for fichier in `ls $1*.txt`
        do
            echo "--------------------------------------"
            echo $fichier
            new_fichier=(${fichier//\// })
            new_fichier=(${new_fichier[1]//./ })
            echo ${new_fichier[0]}

            python3 mwe_coref.py ./$1ofcors_outputs/${new_fichier[0]}_mentions_output.json ./$1${new_fichier[0]}annote.config48.cupt
        done
}

if [ $2 == "-os" ]
then
    mkdir ./$1ofcors_outputs/
    echo "OFCORS"
    ofcors "$1"
    echo "PYTHON"
    mwecoref "$1"
    python3 statistiques.py $1mwecoref_outputs/
elif [ $2 == "-o" ]
then
    mkdir ./$1ofcors_outputs/
    ofcors "$1"
elif [ $2 == "-s" ]
then
    mkdir ./$1mwecoref_outputs/
    mwecoref "$1"
    python3 statistiques.py $1mwecoref_outputs/
else
    echo "Cette option n'existe pas. "
    echo "-o : lance ofcors-infer"
    echo "-s : lance mwe_coref.py"
    echo "-os : lance ofcors-infer et mwe_coref.py"
fi
