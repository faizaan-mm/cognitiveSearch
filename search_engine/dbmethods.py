# import pdfextract as pdf 
import mysql.connector
import os
from os.path import join, dirname
from dotenv import load_dotenv
import sys

# if not sys.warnoptions:
#     import warnings
#     warnings.simplefilter("ignore")
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

config = {
  'user': os.environ.get("user"),
  'password': os.environ.get("password"),
  'host': '127.0.0.1',
  'database': os.environ.get("database"),
  'raise_on_warnings': True
}

def insertLink(link,type_of_url='',title=''):
	cnx = mysql.connector.connect(**config)
	cursor = cnx.cursor()
	sql = "select urlid from urls where link = '%s';"%(link)
	cursor.execute(sql)
	data = cursor.fetchall()
	if len(data)==0:
		if type_of_url == '':
			sql = "insert into urls (link,title) values ('%s','%s');"%(link,title)
		else:
			sql = "insert into urls (link,type,title) values ('%s','%s','%s');"%(link,type_of_url,title)
		cursor.execute(sql)
		cnx.commit()
	else:
		return data[0][0]
	sql = "select urlid from urls where link = '%s'"%(link)
	cursor.execute(sql)
	data = cursor.fetchall()
	return data[0][0]
	cnx.close()

def insertKeywords(keywords,urlid):
	sql = "insert into maps values ('%s',%s,%s);"
	cnx = mysql.connector.connect(**config)
	cursor = cnx.cursor()
	for k in keywords:
		# print(sql%(k[0],urlid,k[1]))
		try:
			cursor.execute(sql%(k[0],urlid,k[1]))
		except:
			continue
	cnx.commit()

# if __name__ == '__main__':
# 	insertLink('./pdfs/ram.pdf','PDF')
