import history

import sqlite3
urls = []
from boilerpipe.extract import Extractor
conn = sqlite3.connect('/home/ramrathi/History')
c = conn.cursor()
x = 0
for i in c.execute('select url from urls where id > 68900'):
	try:
		urls.append(i[0])
		if not i[0].startswith("https://www."):
			continue
		history.websitePipeline(i[0])
		print("done: ",i[0])
		x+=1
	except(e):
		print(e)
		continue
