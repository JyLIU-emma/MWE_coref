tokens_ofcors = {"0":"Le", "1":"week", "2":"-", "3":"end", "4":"a", "5":"passé", "6":".", "7":"Mr.", "8":"aime", "9":"Paris."} #token_o
tokens_cupt = {"0":"Le", "1":"week-end", "2":"a", "3":"passé", "4":".", "5":"Mr", "6":".", "7":"aime", "8":"Paris", "9":"."} #token
mention = {"1":{"CONTENT":["week", "-", "end"], "START":"1", "END":"3"}, "2":{"CONTENT":["Paris."], "START":"9", "END":"9"}}

def tokenisation_unify(tokens_ofcors, tokens_cupt):
    i = 0
    i_o = 0
    # dico = {}
    dico_o = {}
    while i < len(tokens_cupt):
        token = tokens_cupt.get(str(i))
        # print(i, token)
        token_o = tokens_ofcors.get(str(i_o))
        # chaine identique
        if token == token_o:
            # dico[str(i)] = [str(i_o)]
            dico_o[str(i_o)] = [str(i)]
        # chaine non identique
        else:
            if len(token) == len(token_o):
                print("chaine de caractere differente, ne peut rien faire")
                break
            else:  # longueur differentes
                if len(token) > len(token_o):

                    while len(token) > len(token_o):
                        # if not dico.get(str(i)):
                            # dico[str(i)] = [str(i_o)]
                        # else:
                            # dico[str(i)].append(str(i_o))
                        ###########
                        dico_o[str(i_o)] = [str(i)]

                        i_o += 1
                        token_o = token_o + tokens_ofcors.get(str(i_o))
                    if len(token) != len(token_o) or token != token_o:
                        print(f"token:{token}\ttoken_o:{token_o}")
                        print("chaine de caractere combinee toujours differente, ne peut rien faire")
                        break
                    elif token == token_o:
                        # dico[str(i)].append(str(i_o))

                        dico_o[str(i_o)] = [str(i)]

                else:  #  len(token) < len(token_o)
                    while len(token) < len(token_o):
                        ##############
                        if not dico_o.get(str(i_o)):
                            dico_o[str(i_o)] = [str(i)]
                        else:
                            dico_o[str(i_o)].append(str(i))

                        # dico[str(i)] = [str(i_o)]
                        i += 1
                        token = token + tokens_cupt.get(str(i))
                    
                    if len(token) != len(token_o) or token != token_o:
                        print(f"token:{token}\ttoken_o:{token_o}")
                        print("chaine de caractere combinee toujours differente, ne peut rien faire")
                        break
                    elif token == token_o:
                        # dico[str(i)] = [str(i_o)]
                        ##########
                        dico_o[str(i_o)].append(str(i))
        i += 1
        i_o += 1
    return dico_o

print("---------")
# print(dico)  # {'0': ['0'], '1': ['1', '2', '3'], '2': ['4'], '3': ['5'], '4': ['6'], '5': ['7'], '6': ['7'], '7': ['8'], '8': ['9'], '9': ['9']}
dico_o = tokenisation_unify(tokens_ofcors, tokens_cupt)
print(dico_o)  # {'0': ['0'], '1': ['1'], '2': ['1'], '3': ['1'], '4': ['2'], '5': ['3'], '6': ['4'], '7': ['5', '6'], '8': ['7'], '9': ['8', '9']}

for ment in mention.values():
    i_start = min([int(i) for i in dico_o.get(ment["START"])])
    ment["START"] = i_start
    i_end = max([int(i) for i in dico_o.get(ment["END"])])
    ment["END"] = i_end

print(mention)  # {'1': {'CONTENT': ['week', '-', 'end'], 'START': 1, 'END': 1}, '2': {'CONTENT': ['Paris.'], 'START': 8, 'END': 9}}
print(int(int("6")))