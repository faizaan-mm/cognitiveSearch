import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
import slate3k as slate
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


def remove_stop1(sentence):
    # sentence is a list of words entered by the user
    stop = set(stopwords.words('english'))
    # print(w)
    # print(len(stopwords))
    file = open("english", "r")
    list2 = []
    for word in file:
        list2.append(word)
    # print(len(list2))
    new_stopwords = stop.union(list2)
    # print(len(new_stopwords))
    result = []
    for word in sentence:
        if word not in new_stopwords:
            result.append(word)

    return result

def remove_stop(text):
    wordTokens = word_tokenize(text)
    wordTokens = [x.lower() for x in wordTokens]
    punctuations = ['(',')',';',':','[',']',',','.','!','?','/','"',"'",'-','\\n','>','<','&']
    stopWords = stopwords.words('english')
    keywords = [word for word in wordTokens if not word in stopWords and not word in punctuations]
    return keywords

