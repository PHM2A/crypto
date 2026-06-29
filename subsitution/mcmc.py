import numpy as np
ascii_decalage=97



def charToindex(c):
    """Convert a character to its index (0-26"""
    if c == " ":
        return 0
    return ord(c.lower()) - ascii_decalage + 1

def indexToChar(i):
    """Convert an index (0-26 to its character"""
    if i == 0:
        return " "
    return chr(i + ascii_decalage -1 )

def normalisationData(c):
    c=c.lower()
    
    if(c == chr(339)):
        return "oe"
   
    to_A = [192,224,226]
    to_C = [199,231]
    to_E = [200,201,202,232,233,234,235]
    to_I = [238,239]
    to_O = [244]
    to_U = [249,251,252]
    to_SPACE = list(range(33,65)) + [171,187,8217,8230]
    
    

    c2 = c
    # if(ord(c2) in range(97,123)):
    #     c2 = chr(ord(c2)-32)
    if ord(c2) in to_SPACE:
        c2 = " "
    if ord(c2) in to_A:
        c2 = "a"
    if ord(c2) in to_C:
        c2 = "c"
    if ord(c2) in to_E:
        c2 = "e"
    if ord(c2) in to_I:
        c2 = "i"
    if ord(c2) in to_O:
        c2 = "o"
    if ord(c2) in to_U:
        c2 = "u"  
   
    
    return c2


def get_whole_text(fic):
    """Return whole text"""
    whole_text = ""
    with open(fic, "r", encoding="utf-8") as file:
        text = file.read()
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = text.replace("  ", " ")
    for c in text:
        c = normalisationData(c)
        if c != "":
            whole_text += c
    return whole_text

def getFrequency(text):
    frequency =np.array([[i,0] for i in range(27)])
    for i in range(len(text)):
        c1 = charToindex(text[i])      
        frequency[c1][1] += 1    
    indices = np.argsort(frequency[:, 1])
    # Tableau trié
    freq = frequency[indices]
    return freq

def get_data(fic):
    """Return the data matrix"""
    data = np.zeros((27,27))
    frequency =np.array([[i,0] for i in range(27)])
    whole_text = get_whole_text(fic)
    # print(whole_text.count("a"))
    for i in range(len(whole_text) - 1):
        c1 = charToindex(whole_text[i])
        c2 = charToindex(whole_text[i + 1])
        data[c1][c2] += 1
        frequency[c1][1] += 1

    data = [data[i] / np.sum(data[i]) for i in range(27)]
    indices = np.argsort(frequency[:, 1])

    # Tableau trié
    freq = frequency[indices]
    return data,freq

def crypt(text,solution):
    """Crypt the text with the solution"""
    crypted_text = ""
    for c in text:
        
        index = charToindex(normalisationData(c))
        crypted_text += indexToChar(solution[index])
    return crypted_text

def notation(text,data):
    n = 0
    
    for i in range(len(text) - 1):
        n = n+np.log(data[charToindex(normalisationData(text[i]))][charToindex(normalisationData(text[i + 1]))]+1e-6)
    # return n/(np.mean(data)*(len(text) - 1))
    return n/len(text)

def count_correct_words(s, dictionnary_words):
    cnt = 0
    word_list = s.split(" ")
    for w in word_list:
        if w in dictionnary_words:
            cnt +=1
    return cnt, len(word_list)

def score_correct_words(s, dictionnary_words):
    res = 0
    tot = 0
    word_list = s.split(" ")
    for w in word_list:
        if w in dictionnary_words:
            res += len(w)
        tot += len(w)
    return res/tot

def find_wrong_words(s, dictionnary_words):
    word_list = s.split(" ")
    for w in word_list:
        if w not in dictionnary_words:
            print(w)

BEST = -2.05
MIN_ITER = 2000
def mcmc(text):
    """ algorithm to find the best text"""
    # data = get_data("swann.txt")
    e= 0.05
    data,freq_base = get_data("swann.txt")
   
    best_text = text
    best_score = notation(text,data)
    solution = np.array([i for i in range(27)])
    freq_text = getFrequency(text)
    for i in range(27):
        solution[[freq_text[i][0]]] = freq_base[i][0]
    # np.random.shuffle(solution)
    # return crypt(text, solution)
    new_score = 0
    new_text = ""
    best_solution = solution.copy()
    print(notation(crypt(text, solution),data))
    for i in range(50000):
        # Randomly change a character in the text
        index = np.random.choice(range(27),2)
        new_solution = solution.copy()
        new_solution[index[0]], new_solution[index[1]] = solution[index[1]], solution[index[0]]
        new_text = crypt(text, new_solution)
        # # Calculate the score of the new text
        new_score = notation(new_text,data)
        if new_score > BEST and i > MIN_ITER:
            # return new_text, new_score
            break
        
        if new_score > best_score :           
           
            best_text = new_text
            best_score = new_score
            solution = new_solution.copy()
            best_solution = solution.copy()
        else:
            if (best_score - new_score) < 0.05:
                if np.random.rand() < e:
                    solution = new_solution.copy()
    print("phase 1 done")
    print(best_text,best_score)  

    dictionnary_words = get_whole_text('swann.txt').split(" ")
    solution = best_solution.copy()
    
    best_score = 4*score_correct_words(best_text, dictionnary_words) + notation(best_text,data)
    print("best score", best_score)
    for i in range(2000):
        # Randomly change a character in the text
        index = np.random.choice(range(27),2)
        new_solution = solution.copy()
        new_solution[index[0]], new_solution[index[1]] = solution[index[1]], solution[index[0]]
        new_text = crypt(text, new_solution)
        # # Calculate the score of the new text
        new_score = 4*score_correct_words(new_text, dictionnary_words) + notation(new_text,data)
       
        
        if new_score > best_score :           
            # print(index,solution,new_solution)
            best_text = new_text
            best_score = new_score
            solution = new_solution.copy()
            # print("new best score", best_score,best_text,notation(best_text,data))
        else:
            if (best_score - new_score) < 0.05:
                if np.random.rand() < e:
                    solution = new_solution.copy()
     
    return best_text, best_score




solution = np.array([i for i in range(27)])
np.random.shuffle(solution)
txt = "bonjour tout le monde, comment ca va aujourd'hui ?"
txt="Elles sont également limitées par la taille de l’échantillon, puisqu’elles deviennent insolubles lorsque ceux-ci sont trop grands"
# txt="Les méthodes de Monte-Carlo sont particulièrement utilisées pour calculer des intégrales en dimensions plus grandes que un en particulier, pour calculer des surfaces et des volumes. Elles sont également couramment utilisées en physique des particules, où des simulations probabilistes permettent d'estimer la forme d'un signal ou la sensibilité d'un détecteur. La comparaison des données mesurées à ces simulations peut permettre de mettre en évidence des caractéristiques inattendues, par exemple de nouvelles particules. "
# txt = "Longtemps, je me suis couché de bonne heure. Parfois, à peine ma bougie éteinte, mes yeux se fermaient si vite que je n'avais pas le temps de me dire: «Je m'endors.» Et, une demi-heure après, la pensée qu'il était temps de chercher le sommeil m'éveillait; je voulais poser le volume que je croyais avoir encore dans les mains et souffler ma lumière"
# txt="l'algorithme de Metropolis consiste en une marche aléatoire avec une correction afin que chaque nouvelle valeur extraite puisse être rejetée si elle correspond à une valeur de la fonction d'intégration plus petite que le point précédent, avec une probabilité égale à un, moins le rapport entre ces valeurs"
print(txt)
txt = crypt(txt, solution)
print(txt)

print(mcmc(txt))
