import numpy as np
import dbmethods
import mysql.connector
import os
from os.path import join, dirname
from dotenv import load_dotenv
from itertools import combinations 
import sys
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer

def extractSingleRoot(keyword):
    stemmer = SnowballStemmer("english")
    return stemmer.stem(keyword)

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

config = {
  'user': os.environ.get("user"),
  'password': os.environ.get("password"),
  'host': '127.0.0.1',
  'database': os.environ.get("database"),
  'raise_on_warnings': True
}

def rSubset(arr, r): 
    return list(combinations(arr, r)) 

def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    return (matrix[size_x - 1, size_y - 1])


# DO NOT TOUCH THIS FUNCTION IT WILL LITERALLY BREAK
def search(search_keywords):
	cnx = mysql.connector.connect(**config)
	search_keywords = list(set(search_keywords))
	cursor = cnx.cursor()
	all_sets = dict()
	for k in search_keywords:
		stemmed_k = extractSingleRoot(k)
		all_sets[stemmed_k] = set()
		sql = "select keyword,link,title from urls natural join maps where keyword like '" + stemmed_k + "%'"
		cursor.execute(sql)
		data = cursor.fetchall()
		for d in data:
			# print((d[0],d[1],k,levenshtein(k,stemmed_k)))
			all_sets[stemmed_k].add((d[1]))
	print(all_sets)
	result = []
	total_keywords = len(search_keywords)
	for i in range(total_keywords):
		chosen_keywords = rSubset(search_keywords,total_keywords-i)
		for each_set in chosen_keywords:
			each_set = [extractSingleRoot(x) for x in each_set]
			# print(each_set)
			temp_result = set()
			temp_result = all_sets[each_set[0]]
			for x in each_set:
				temp_result = temp_result.intersection(all_sets[x])
			for x in temp_result:
				if x not in result: 
					result.append(x)
	print(each_set)
	return result

def searchv2(search_keywords):
	# Input is ['keywrod1','keyword2']
	# The keywords should be stemmed and parsed to remove stop words
	# To stem each word, you can use pdfextract.extractSingleRoot('myword') which returns the stemmed version
	cnx = mysql.connector.connect(**config)
	search_keywords = list(set(search_keywords))
	cursor = cnx.cursor()
	flag = 0
	sql = "SELECT link,((sum(score)+10*count(keyword))) as final_score, title, urlid FROM cogsearch.maps natural join cogsearch.urls where "
	sql2 = "SELECT link,keyword FROM cogsearch.maps natural join cogsearch.urls where "
	for k in search_keywords:
		if flag ==0:
			flag = 1
		else:
			sql+=' or '
			sql2+=' or '
		stemmed_k = extractSingleRoot(k)
		sql+="keyword like '" + stemmed_k + "%'"
		sql2+="keyword like '" + stemmed_k + "%'"
	sql2+=" order by link;"	
	sql+=" group by urlid order by final_score desc;"
	cursor.execute(sql)
	initial_scores = cursor.fetchall()
	cursor.execute(sql2)
	keyword_mappings = cursor.fetchall()
	link_to_key = dict()
	link_to_score = dict()
	for link in initial_scores:
		link_to_score[link[0]] = link[1]
	for mapping in keyword_mappings:
		link = mapping[0]
		keyword = mapping[1]
		link_to_key.setdefault(link,[]).append(keyword)

	print(link_to_score)
	# Levenshit distance
	for link in link_to_key:
		leven_score = 0
		for key in link_to_key[link]:
			min_leven = 100
			for word in search_keywords:
				l = levenshtein(key,word)
				min_leven = min(min_leven,l)
			leven_score+=min_leven

	sorted_scores = reversed(sorted(link_to_score.items(), key=lambda kv: kv[1]))
	for x in sorted_scores:
		print(x[0])
	return initial_scores

def searchv3(search_keywords):
	cnx = mysql.connector.connect(**config)
	search_keywords = list(set(search_keywords))
	cursor = cnx.cursor()
	flag = 0
	sql = "SELECT link,(sum(score)/count(score)) as final_score, title, urlid FROM cogsearch.maps natural join cogsearch.urls where "
	sql2 = "SELECT link,keyword,title FROM cogsearch.maps natural join cogsearch.urls where "
	for k in search_keywords:
		if flag ==0:
			flag = 1
		else:
			sql+=' or '
			sql2+=' or '
		stemmed_k = extractSingleRoot(k)
		sql+="keyword like '%" + stemmed_k + "%'"
		sql2+="keyword like '%" + stemmed_k + "%'"
	sql2+=" order by link;"	
	sql+=" group by urlid order by final_score desc;"
	
	cursor.execute(sql)
	initial_scores = cursor.fetchall()

	cursor.execute(sql2)
	keyword_mappings = cursor.fetchall()

	link_to_key = dict()
	link_to_score = dict()
	link_to_title = dict()

	for link in initial_scores:
		link_to_score[link[0]] = link[1]

	for link in initial_scores:
		link_to_title[link[0]] = link[2]

	for mapping in keyword_mappings:
		link = mapping[0]
		keyword = mapping[1]
		link_to_key.setdefault(link,[]).append(keyword)

	for link in link_to_key:
		count = 0
		for search_key in search_keywords:
			for word in link_to_key[link]:
				if search_key in word:
					count+=1
					break
		link_to_score[link]+=(10*count)
	
	# Levenshit distance
	for link in link_to_key:
		leven_score = 0
		for key in link_to_key[link]:
			min_leven = 100
			for word in search_keywords:
				l = levenshtein(key,word)
				min_leven = min(min_leven,l)
			leven_score+=min_leven
		# print(link,len(link_to_key[link]))
		leven_score/=len(link_to_key[link])
		# print(link,leven_score)
		link_to_score[link]/=(1+0.01*leven_score)

	for link in link_to_title:
		count = 0
		for search_word in search_keywords:
			if search_word in link_to_title[link] or search_word in link:
				count+=1
		link_to_score[link]*=(1+0.5*count)

	sorted_scores = reversed(sorted(link_to_score.items(), key=lambda kv: kv[1]))
	# for x in sorted_scores:
	# 	print(x)
	return list(sorted_scores)
