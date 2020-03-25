#!/usr/bin/env python3
import PyPDF2
import textract
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
import slate3k as slate
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from PIL import Image
import dbmethods as db
import glob
import sys
import os


def getFullPath(link):
    return os.path.abspath(link)

def is_number(n):
    try:
        float(n)   
    except ValueError:
        return False
    return True

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

# So we're stemming the users entered keywords cause its fine if they overstem since we're using a hacking sql like solution, but we dont overstem the stored keywords thus lemmanize

def extractSingleRoot(keyword):
    stemmer = SnowballStemmer("english")
    return stemmer.stem(keyword)

def extractRoots(keywords):
    roots = []
    lemmatizer = WordNetLemmatizer() 
    roots = [lemmatizer.lemmatize(keyword) for keyword in keywords]
    return roots

def extractPdfImage(pdf=''):
    input1 = PyPDF2.PdfFileReader(open(pdf, "rb"))
    totalPageNumber = input1.numPages
    currentPageNumber = 0

    while(currentPageNumber<totalPageNumber):
        page0 = input1.getPage(currentPageNumber)
        if '/XObject' in page0['/Resources']:
            xObject = page0['/Resources']['/XObject'].getObject()

            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                    data = xObject[obj].getData()
                    if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                        mode = "RGB"
                    else:
                        mode = "P"
                    
                    if '/Filter' in xObject[obj]:
                        if xObject[obj]['/Filter'] == '/FlateDecode':
                            img = Image.frombytes(mode, size, data)
                            img.save(obj[1:] + ".png")
                        elif xObject[obj]['/Filter'] == '/DCTDecode':
                            img = open(obj[1:] + ".jpg", "wb")
                            img.write(data)
                            img.close()
                        elif xObject[obj]['/Filter'] == '/JPXDecode':
                            img = open(obj[1:] + ".jp2", "wb")
                            img.write(data)
                            img.close()
                        elif xObject[obj]['/Filter'] == '/CCITTFaxDecode':
                            img = open(obj[1:] + ".tiff", "wb")
                            img.write(data)
                            img.close()
                    else:
                        img = Image.frombytes(mode, size, data)
                        img.save(obj[1:] + ".png")
        else:
            print("No image found.")
        currentPageNumber+=1

def extractPdfText(filePath=''):

    with open(filePath,'rb') as f:
        extracted_text = slate.PDF(f)
    text = ((str(extracted_text)))
    # print(type(text))
    text = text.replace('\\n',' ')
    if(len(text) < 20): # Hoping that even the smallest textual pdf has more than 20 characters 
        # OCR this crap
        text = textract.process(filePath, method='tesseract', encoding='utf-8')
    return text


def extractKeywordList(pdfFilePath):
    pdfText = extractPdfText(pdfFilePath)
    keywords = []
    try:
        keywords = extractKeywords(pdfText.decode('utf-8'))
    except(UnicodeDecodeError, AttributeError):
        keywords = extractKeywords(pdfText)
    roots = extractRoots(keywords)
    keywords = keywordImportance(roots)
    keywords = sorted(keywords.items(), key=lambda x: x[1],reverse = True)
    return keywords

def extractKeywords(text):
    wordTokens = word_tokenize(text)
    wordTokens = [x.lower() for x in wordTokens]
    punctuations = ['(',')',';',':','[',']',',','.','!','?','/','"',"'",'-','\\n','>','<','&']
    stopWords = stopwords.words('english')
    keywords = [word for word in wordTokens if not word in stopWords and not word in punctuations]
    return keywords

def pdfPipeline(pdfFilePath):
    pdfFilePath = getFullPath(pdfFilePath)
    keywords =  extractKeywordList(pdfFilePath)
    title = pdfFilePath.split('/')[-1].split('.')[0]
    urlid = db.insertLink(pdfFilePath,"PDF",title)
    db.insertKeywords(keywords,urlid)

# if __name__ == '__main__':
#     files = glob.glob("./pdfs/*.pdf")
#     i = 1
#     for pdfFilePath in files:
#         print(pdfFilePath)
#         print(i,'/',len(files))
#         i+=1
#         try:
#             pdfPipeline(pdfFilePath)
#         except:  
#             continue    

# pdfPipeline(sys.argv[1])

# getHilight('./pdfs/Astraea.pdf')