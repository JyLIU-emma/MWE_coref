#!/bin/bash
# Anaëlle Pierredon et Jianying Liu

# ./lanceur.sh -os phrases/ [fichier_resultats]
# Dans phrases/ se trouve les fichiers txt à analyser par OFCORS
# La sortie d'OFCORS se trouve dans phrases/ofcors_outputs/
# La sortie de merge_s2s_ofcors se trouve dans phrases/mwecoref_outputs/
# Le fichier de résultats est optionnel

ofcors()
{
    for fichier in `ls $1*.txt`
        do
            echo "--------------------------------------"
            echo $fichier
            ofcors-infer -f -k stanza -p window --window-size 8 $fichier

            new_fichier=(${fichier//\// })
            dernier=$((${#new_fichier[@]}-1))
            new_fichier=(${new_fichier[dernier]//./ })
            echo $new_fichier

            mv ./ofcors_outputs/resulting_chains.json ./$1ofcors_outputs/${new_fichier}_resulting_chains.json
            mv ./ofcors_outputs/mentions_detection/mentions_output.json ./$1ofcors_outputs/${new_fichier}_mentions_output.json
            mv ./ofcors_outputs/mentions_detection/tokens.json ./$1ofcors_outputs/${new_fichier}_tokens.json
        done
}

mwecoref()
{
    for fichier in `ls $1*.txt`
        do
            echo "--------------------------------------"
            echo $fichier
            new_fichier=(${fichier//\// })
            dernier=$((${#new_fichier[@]}-1))
            new_fichier=(${new_fichier[dernier]//./ })
            echo $new_fichier
            if [[ `ls ./$1$new_fichier*.cupt` =~ ./$1$new_fichier.cupt ]]
            then
                python3 merge_s2s_ofcors.py ./$1 $new_fichier ./$1${new_fichier}.cupt
            else
                python3 merge_s2s_ofcors.py ./$1 $new_fichier ./$1${new_fichier}_annote.config48.cupt
            fi
        done
}

if [ $1 == "-os" ]
then
    mkdir ./$2ofcors_outputs/
    echo "OFCORS"
    ofcors "$2"
    echo "PYTHON"
    mkdir ./$2mwecoref_outputs/
    mwecoref "$2"
    if [ $3 ]
    then
        python3 statistiques.py $2mwecoref_outputs/ -out $3
    else
        python3 statistiques.py $2mwecoref_outputs/
    fi
elif [ $1 == "-o" ]
then
    mkdir ./$2ofcors_outputs/
    ofcors "$2"
elif [ $1 == "-s" ]
then
    mkdir ./$2mwecoref_outputs/
    mwecoref "$2"
    if [ $3 ]
    then
        python3 statistiques.py $2mwecoref_outputs/ -out $3
    else
        python3 statistiques.py $2mwecoref_outputs/
    fi
else
    echo " Cette option n'existe pas. "
    echo " -o : lance ofcors-infer "
    echo " -s : lance merge_s2s_ofcors.py et statistiques.py "
    echo " -os : lance ofcors-infer, merge_s2s_ofcors.py et statistiques.py "
fi
