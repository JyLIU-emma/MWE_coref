# exemple of use in terminal:
# python3 udpipe_annote.py ../INPUT/FR/new_corpus.txt ../INPUT/FR/new_corpus.cupt http://corpus/uri

import sys
from ufal.udpipe import Model, Pipeline, ProcessingError
import glob
import os
import re

# load the model
sys.stderr.write('Loading model: ')
model = Model.load("model_udpipe/french-gsd-ud-2.5-191206.udpipe")
if not model:
    sys.stderr.write("Cannot load model")
    sys.exit(1)
sys.stderr.write('done\n')

def find_all_files_path(path,extension="txt"):
    """
    return a list of input file(s) in the given path
    default: txt files
    """
    if os.path.isfile(path):
        return [path]
    elif os.path.isdir(path):
        return glob.glob(f"{path}/**/*.{extension}", recursive=True)

def load_file(path_inputfile):
    """
    Load the file txt.
    """
    with open(path_inputfile, "r", encoding="utf8") as inputfile:
        text = inputfile.read()
    return text

def annote_with_udpipe(text):
    """
    Annotate the txt text, return the result in conllu format
    """
    pipeline = Pipeline(model, "tokenize", Pipeline.DEFAULT, Pipeline.DEFAULT, "conllu")
    error = ProcessingError()
    # Process data
    text_conllu = pipeline.process(text, error)
    if error.occurred():
        sys.stderr.write("An error occurred when running run_udpipe: ")
        sys.stderr.write(error.message)
        sys.stderr.write("\n")
        sys.exit(1)
    return text_conllu


def transform_to_cupt_blind(text_conllu, uri, file_path, sent_id):
    """
    transform the conllu text into cupt format
    TODO: sent_id now use simple increment, possibly need more complicated format
    """
    lines = text_conllu.split("\n")
    new_lines = []
    liste_test=[]
    for i in lines:
        if i != "":
            if i[0] == "#":
                if i in ["# newpar", "# newdoc"]:
                    continue
                if i[:9] == "# sent_id":
                    i = f"# source_sent_id = {uri} {file_path} {sent_id}"
                    sent_id += 1
            else:
                i = i + "\t_"
        new_lines.append(i)
    text_cupt = "\n".join(new_lines)
    return text_cupt, sent_id

def write_to_file(text, output_path, add=True):
    """
    write the text into the given path
    """
    if add:
        with open(output_path, "a", encoding="utf8") as output:
            output.write(text)
    else:
        with open(output_path, "w", encoding="utf8") as output:
            output.write(text)

def file_txt2cupt(input_path, output_path, corpus_uri):
    """
    a complite process from txt file to cupt file

    Args:
        input_path(str): the path to txt file/ txt files directory
        output_path(str): the path to write our new cupt file
        corpus_uri(str): use to write the uri of corpus in source_sent_id
    """
    sent_id = 1
    first_line = "# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC PARSEME:MWE\n"
    write_to_file(first_line, output_path, add=False)
    parent_dir = input_path.split("/")[:-1]
    parent_dir = "/".join(parent_dir)
    for file_path in find_all_files_path(input_path):
        corpus_intern_path = re.sub(parent_dir+"/","",file_path)
        write_to_file(f"# newdoc = {corpus_intern_path}\n", output_path)     ###### do we need this line?
        text = load_file(file_path)
        text_conllu = annote_with_udpipe(text)
        text_cupt, sent_id = transform_to_cupt_blind(text_conllu, corpus_uri, corpus_intern_path, sent_id)
        write_to_file(text_cupt, output_path)

if __name__ == "__main__":
    # corpus_uri = "http://my/newcorpus/uri"
    file_txt2cupt(sys.argv[1], sys.argv[2], sys.argv[2])   # input output uri



