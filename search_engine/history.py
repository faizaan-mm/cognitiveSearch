import sqlite3
from boilerpipe.extract import Extractor
from bs4 import BeautifulSoup as bs
import requests
import dbmethods as db
import PyPDF2
import textract
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
import slate3k as slate
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from PIL import Image
import glob
import sys
import os


def extractRoots(keywords):
    roots = []
    lemmatizer = WordNetLemmatizer() 
    roots = [lemmatizer.lemmatize(keyword) for keyword in keywords]
    return roots


def extractKeywords(text):
    wordTokens = word_tokenize(text)
    wordTokens = [x.lower() for x in wordTokens]
    punctuations = ['(',')',';',':','[',']',',','.','!','?','/','"',"'",'-','\\n','>','<','&']
    stopWords = stopwords.words('english')
    keywords = [word for word in wordTokens if not word in stopWords and not word in punctuations]
    return keywords


def keywordImportance(keywords):
    keys = dict()
    total = 0
    for k in keywords:
        if len(k) < 3 or is_number(k) or k.startswith('\\') or not k[0].isalpha():
            continue
        total+=1
        keys[k] = keys.get(k,0) + 1
    for k in keys:
        keys[k] = keys[k]/total
    return keys

def extractWebsiteKeywords(link):
	try:
		extractor = Extractor(extractor='ArticleExtractor', url=link)
		keywords = extractKeywords(extractor.getText())
		roots = extractRoots(keywords)
		keywords = keywordImportance(roots)
		keywords = sorted(keywords.items(), key=lambda x: x[1],reverse = True)
		return keywords
	except:
		return

def getWebsiteTitle(link):
	try:
		r = requests.get(link)
		soup = bs(r.content, 'lxml')
		return soup.select_one('title').text
	except:
		return ''


def websitePipeline(link):
	print(link)
	link = link.strip(' \n')
	title = getWebsiteTitle(link)
	keywords = extractWebsiteKeywords(link)
	try:
		urlid = db.insertLink(link,'HTM',title)
		if keywords:
			db.insertKeywords(keywords,urlid)
	except:
		return
def cronchecker(filename):
	print("HEREEE",filename)
	f = list(open(filename,'r'))
	url = f[0]
	content = f[2]
	websitePipeline(url)
	
# cronchecker("data.txt")