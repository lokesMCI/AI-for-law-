#import nltk
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import spacy
import os
from flask import Flask, flash, request, redirect, render_template, Markup, render_template_string
from werkzeug.utils import secure_filename
from spacy.tokenizer import Tokenizer
from string import punctuation
import pymongo
from pymongo import MongoClient
from threading import Thread

import time
from time import gmtime, strftime




print('started')
cluster = pymongo.MongoClient("mongodb+srv://lokesmci:lokes%40mongodb2025@nebula-cluster.4xrhdqy.mongodb.net/?retryWrites=true&w=majority")
db = cluster['nebula-cluster']
print('connected to db')


nlp = spacy.load("en_core_web_sm")
tokenizer = Tokenizer(nlp.vocab)

app=Flask(__name__)


def plot(my_data, my_labels):
    # os.remove('static/images/piechart.png')
    print("before plotting")
    p = plt.pie(my_data, labels=my_labels, autopct='%1.1f%%', startangle=15, shadow=True)#, colors=my_colors, explode=my_explode)
    print("after plotting")
    plt.title('Important keywords')
    p = plt.axis('equal')
    # plt.show()
    print('before saving plt')
    p= plt.savefig('static/images/piechart.png')
    print('after saving plt')

app.secret_key = strftime(time.ctime())
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    imageList = os.listdir('static/images')
    imagelist = ['images/' + image for image in imageList]
    app.secret_key = strftime(time.ctime())
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    return render_template("index.html")
    #return render_template('index.html',)

@app.route('/piechart.html', methods=['GET','POST'])
def view_pie():
    imageList = os.listdir('static/images')
    imagelist = ['images/' + image for image in imageList]
    app.secret_key = strftime(time.ctime())
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    return render_template("piechart.html")


@app.route('/', methods=['POST','GET'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            f = open('uploads/'+ filename)
            txt = f.read()
            tokens = tokenizer(txt)
           

            doc = nlp(txt.lower())
            result = []
            pos = []
            pos_tag = ['PROPN', 'NOUN'] 
            doc = nlp(txt.lower()) 
            for token in doc:
                #print(token.pos_)
                if(token.text in nlp.Defaults.stop_words or len(token.text)<4 or token.text in punctuation or token.text in [';',')','(','[',']'] or token.text in [str(i) for i in range(10)]):
                    continue
                if(token.pos_ in pos_tag):
                    result.append(token.text.rstrip().lower())
                    pos.append(token.pos_)
            result = list(set(result))

            js = []
            for res,p in zip(result,pos):
                d = {'_id':res, 'count':txt.lower().count(res), 'pos':p}
                js.append(d)
            #print(js)
            js_sorted = sorted(js, key=lambda d: d['count'],reverse=True) 
            coll = filename+strftime(time.ctime())
            collection = db[coll]
            print('db created')
            collection.insert_many(js_sorted)
            print('inserted into collection')

            my_data = [d['count'] for d in js_sorted[:10]]
            my_labels = [d['_id'] for d in js_sorted[:10]]#'Tasks Pending', 'Tasks Ongoing', 'Tasks Completed'
            #print(js_sorted)
            #my_colors = ['lightblue', 'lightsteelblue', 'silver']
            #my_explode = (0, 0.1, 0)
            print("before plotting")
            ##plot(my_data,my_labels)
            #thread = Thread(target=plot,args=(my_data,my_labels))
            #thread.start()
            #thread.join()
            #
            if os.path.exists("static/images/piechart.png"):
                os.remove('static/images/piechart.png')
            print("before plotting")
            p = plt.pie(my_data, labels=my_labels, autopct='%1.1f%%', startangle=15, shadow=True)#, colors=my_colors, explode=my_explode)
            print("after plotting")
            plt.title('Important keywords')
            p = plt.axis('equal')
            # plt.show()
            print('before saving plt')
            p= plt.savefig('static/images/piechart.png')
            print('after saving plt')
            
            #p = plt.pie(my_data, labels=my_labels, autopct='%1.1f%%', startangle=15, shadow=True)#, colors=my_colors, explode=my_explode)
            #print("after plotting")
            #plt.title('Important keywords')
            #p = plt.axis('equal')
            #plt.show()
            #print('before saving plt')
            #p= plt.savefig('static/images/piechart.png')
            #print('after saving plt')



            #text ="Hai I am here to Demonstrate the actual advantage of flask. Nice to meet you guys."
            #keyword = ["demonstrate","advantage","flask", "you"]
            split = txt.split(" ")

            #ret = map(lambda x: "<b style='color:red;'>" +
            #             x+"</b>" if(x.rstrip().lower() in result) else x, split)
            #output = "<h1 style='font-size:2em;'>The    NLP    OUTPUT:- </h1><br><p style='font-size:2em;'>" + \
            #    " ".join(result) + "</p>"

            #text ="Hai I am here to Demonstrate the actual advantage of flask. Nice to meet you guys."
            #keyword = ["demonstrate","advantage","flask", "you"]
            #split = text.split(" ")

            ret = map(lambda x: "<b style='color:red;'>" +
                         x+"</b>" if(x.lower() in result) else x, split)
            #return "<h1 style='font-size:2em;'>The    NLP    OUTPUT:- </h1><br><p style='font-size:2em;'>"+" ".join(ret) + "</p>"
            app.secret_key = strftime(time.ctime())
            app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
            
            return render_template('Keywords.html',content=Markup(" ".join(ret)))
            # flash(output)
            # return render_template('output.html',output=output)
            #return output
            # return "<p>Got it!</p>"
            # return redirect('/')
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect(request.url)


if __name__ == "__main__":
    app.run(host = '127.0.0.1',port = 5000, debug = False)