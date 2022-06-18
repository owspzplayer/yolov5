import os
import pyodbc
from flask import Flask, request, redirect, url_for
from werkzeug import datastructures
from werkzeug.utils import secure_filename

server = 'owspz' 
database = 'master' 
username = 'sa' 
password = '123456' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

UPLOAD_FOLDER = 'D:/_test/temp'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/postimage/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 
                                   filename))
            return bookinfo('192890')
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

from flask import send_from_directory

@app.route('/bookimage/<filename>')
def getimage(filename):
    file_local = str(filename)
    file_local = file_local[0]+file_local[1]+file_local[2]+"000"
    local='D:/_test/bookimage/'+file_local
    return send_from_directory(local,filename+".jpg")

@app.route('/bookinfo/<mid>')
def bookinfo(mid):
    cursor.execute("SELECT * from books where mid = "+mid+" FOR JSON AUTO")
    row = cursor.fetchone() 
    cursor.execute("update books set readtimes +=1 where mid="+mid)
    return str(row[0])

@app.route('/booksearch/<keyword>')
def bookserech(keyword):
    cursor.execute("select bookname from books where bookname like '%"+ str(keyword)+"%' FOR JSON AUTO")
    row = cursor.fetchone() 
    
    return str(row[0])

@app.route('/foreignlanguage/')
def foreignlanguaged():
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               "foreignlanguage.json")

@app.route('/popular/')
def popular():
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               "popular.json")

@app.route('/googlebc02c96297e30e79.html')
def googlesearch():
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               "googlebc02c96297e30e79.html")

@app.route('/newer/')
def newer():
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               "newer.json")

@app.route('/tital/')
def tital():
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               "main_tiatl_list.json")

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5000 )