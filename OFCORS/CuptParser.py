#/usr/bin/python

#TODO: maintenant: 1 cupt -- 1 fichier; on a besoin de 1 cupt -- plusieurs fichier ?

class Cupt():

    def __init__(self, filepath):
        self.type = "cupt"  #########TODO
        self.lignes = {}
        numero_ligne = 0
        token_i = -1
        with open(filepath, encoding="utf8") as f:
            liste_lignes = f.readlines()
        for ligne in liste_lignes:
            if ligne[0] != "#" and ligne != "\n":
                cols = ligne.split("\t")
                no_token_sent = cols[0]
                token = cols[1]
                if "-" not in no_token_sent:
                    token_i += 1
                    self.lignes[numero_ligne] = Ligne(numero_ligne, str(token_i), ligne.strip(), token)
            else:
                # pour ligne de commentaire: numéro de token : -1
                # TODO: peut etre elargir si on veut traiter sent_id, newdoc
                self.lignes[numero_ligne] = Ligne(numero_ligne, -1, ligne.strip())


                new[numero_ligne] = {"token_i":token_i, "content":ligne.strip()}
            
                # stocker les 2 lignes suivantes répétés 
                match_index = re.match(r"^([0-9]+)-([0-9]+)$", no_token_sent)
                if match_index:
                    token_repete = [match_index.group(1), match_index.group(2)]              
            else:
                new[numero_ligne] = {"token_i": -1, "content":ligne.strip()}        # pour ligne de commentaire: numéro de token: -1
            new[numero_ligne]["mentions"] = []
            numero_ligne += 1



class Ligne():
    def __init__(self, indice, i_token, content, token_form=""):
        self.indice = indice
        self.i_token = i_token
        self.token_form = token_form
        self.content = content
        self.ment_id = []
        self.coref = {}   #dict or list?

