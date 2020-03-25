from flask import *
from stop_words import remove_stop
# from search import *
import pdfextract as pdf
from search import searchv3

app = Flask(__name__)


@app.route('/')
def index():
	return render_template("./index.html")

@app.route('/results', methods=['GET','POST'])
def results():
	search = (request.form['search'].encode('utf-8')).decode('utf-8')
	# print(type(search))	
	# search_list = search.split()

	rmstop = remove_stop(search)
	# rmstop = [str(x.decode('utf-8')) for x in rmstop]
	print("rm_stop list:", rmstop)

	stemmed_list = [str(pdf.extractSingleRoot(x)) for x in rmstop]
	print("stemmed_list: ", stemmed_list)
	a_result = searchv3(stemmed_list)
	print(a_result)
	b_results = a_result[:10]
	
	return render_template("./results.html", results = b_results)

@app.route('/notes', methods=['GET','POST'])
def notes():
	return render_template("./notes.html")

if __name__ == '__main__':
	app.run(debug=True)