#/usr/bin/python3
import sys
from CuptParser import *
from OfcorsFilesParser import *

print("#"*30)
# "./blabla/ofcors_outputs/blabla_mentions_output.json"
rep_corpus = sys.argv[1] # "./blabla/
filename = sys.argv[2]  # blabla
cupt_file = sys.argv[3] # "./blabla/blabla.cupt"
# cupt_file = rep_corpus + filename + ".cupt"

ofcors_rep = rep_corpus + "ofcors_outputs/"
output_rep = rep_corpus + "mwecoref_outputs/"

mention_file = f'{ofcors_rep}{filename}_mentions_output.json'
coref_file = f'{ofcors_rep}{filename}_resulting_chains.json' # "./blabla/ofcors_outputs/blabla_resulting_chains.json"
token_file = f'{ofcors_rep}{filename}_tokens.json' # "./blabla/ofcors_outputs/blabla_tokens.json"

mentions = Mentions(mention_file)
coref = CorefChaines(coref_file)
mentions.chainer(coref.ment_cluster)
ofcors_out = OfcorsOutput(token_file)
ofcors_out.merge_result(mentions)
cupt = Cupt(cupt_file)
cupt.add_ofcors_output(ofcors_out)
cupt.write_to_file(f'{output_rep}{filename}_mwe_coref.cupt')