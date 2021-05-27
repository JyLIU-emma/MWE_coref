# -*- coding: utf-8 -*-
# Jianying Liu et Anaëlle Pierredon

"""
usage :
python merge_s2s_ofcors.py répertoire_corpus txtfilename chemin/vers/cupt
exemple: (on a blabla.txt et blabla.cupt dans ./blabla)
python merge_s2s_ofcors.py ./blabla/ blabla ./blabla/blabla.cupt
"""
import sys
# from CuptParser import Cupt
# from OfcorsFilesParser import Mentions, CorefChaines, OfcorsOutput
from CuptParser import merge_cupt_ofcors

rep_corpus = sys.argv[1]
filename = sys.argv[2]
cupt_file = sys.argv[3]

ofcors_rep = rep_corpus + "ofcors_outputs/"
output_rep = rep_corpus + "mwecoref_outputs/"

mention_file = f'{ofcors_rep}{filename}_mentions_output.json'
coref_file = f'{ofcors_rep}{filename}_resulting_chains.json'
token_file = f'{ofcors_rep}{filename}_tokens.json'

##OLD
# mentions = Mentions(mention_file)
# coref = CorefChaines(coref_file)
# mentions.chainer(coref.ment_cluster)
# ofcors_out = OfcorsOutput(token_file)
# ofcors_out.merge_result(mentions)
# cupt = Cupt(cupt_file)
# cupt.add_ofcors_output(ofcors_out)

##NEW
cupt = merge_cupt_ofcors(cupt_file, token_file, mention_file, coref_file)

cupt.write_to_file(f'{output_rep}{filename}_mwe_coref.cupt')
