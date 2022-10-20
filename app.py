import os
import json
from typing import NewType
import pyodbc
from flask import Flask, request, redirect, url_for
from werkzeug import datastructures
from werkzeug.utils import secure_filename
import cv2
#import detectout
from detectout import detecto
import findbook as fb
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
            img =cv2.imread('D://_test//temp'+'//'+filename)
            a=detecto(img)
            if not a:
                return 'notfoundbook'
            cursor.execute("SELECT * from BookData where lognum like '%"+a[0]['class']+"%' FOR JSON AUTO")
            row = cursor.fetchone() 
            return row[0]
    if request.method == 'GET':
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form action="" method=post enctype=multipart/form-data>
        <p><input type=file name=file>
             <input type=submit value=Upload>
        </form>
        '''

@app.route('/postimage2/', methods=['GET', 'POST'])
def upload_file2():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 
                                   filename))
            img =cv2.imread('D://_test//temp'+'//'+filename)
            a=detecto(img)
            cursor.execute("SELECT * from BookData where lognum like '%"+a[0]['class']+"%' FOR JSON AUTO")
            row = cursor.fetchone() 
      
            return row[0]
    if request.method == 'GET':
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
    file_folder =int(filename)
    file_folder-=file_folder%1000
    local='D:/_test/bookimage/'+str(file_folder)
    locals='D://_test//bookimage//'+str(file_folder)
    if os.path.isfile(locals+'//'+filename+'.jpg'):
        return send_from_directory(local,filename+".jpg")
    else:
        return send_from_directory('D:/_test/bookimage/320000/','320000.jpg')

@app.route('/bookinfo/<mid>')
def bookinfo(mid):
    cursor.execute("SELECT * from BookData where mid like '"+str(mid)+"' FOR JSON AUTO")
    row = cursor.fetchone() 
    cursor.execute("SELECT ISBN from BookData where mid like '"+str(mid)+"'")
    ISBNs = cursor.fetchone() 
    ISBN = str(ISBNs[0]).split('、')
    print(ISBN[0])
    a=str(fb.ISBNimport(ISBN[0]))

    return a

@app.route('/bookinfousers/<randcode>/<mid>')
def bookinfo_users(randcode,mid):

    cursor.execute("SELECT id from member where randcode like '"+str(randcode)+"'")
    userid = cursor.fetchone()

    a = filter(str.isalnum, str(userid[0]))
    users =''.join(list(a))
    cursor.execute("SELECT * from users"+str(users)+" where mid like '"+str(mid)+"' FOR JSON AUTO")
    row = cursor.fetchone()
    
    #cursor.execute("update books set readtimes +=1 where mid="+mid)
    if not row:
        cursor.execute("insert into users"+str(users)+" values ("+str(mid)+",0,0,'');")
        cnxn.commit()
        cursor.execute("SELECT * from users"+str(users)+" where mid like '"+str(mid)+"' FOR JSON AUTO")
        row = cursor.fetchone()
    return str(row[0])
    
@app.route('/booksearchlen/<keyword>')
def bookserechlen(keyword):
    words=keyword.split(' ')
    search=''
    for i,j in enumerate(words):
        search+="bookname like '%"+str(j)+"%' "
        if i!=len(words)-1:
            search +=" and "
    cursor.execute("select count(*) from BookData where "+str(search)+"")
    row = cursor.fetchone()
    a=int(row[0])
    a=(a//10)+1
    return str(a)

@app.route('/booksearch/<keyword>/<page>')
def bookserech(keyword,page):
    words=keyword.split(' ')
    search=''
    for i,j in enumerate(words):
        search+="bookname like '%"+str(j)+"%' "
        if i!=len(words)-1:
            search +=" and "
    cursor.execute("select * from(select ROW_NUMBER() over(order by mid) as rowid,*from BookData where "+str(search)+")as g where rowid between "+str((int(page)*10)-9)+" and "+str(int(page)*10)+" for json auto")
    
    s=''
    while 1:
        row = cursor.fetchone()
        if not row:
            break
        s+=row[0]
    return str(s)

@app.route('/booksearchusers/<keyword>/<page>/<randcode>')
def bookserechusers(keyword,page,randcode):
    cursor.execute("SELECT id from member where randcode like '"+str(randcode)+"'")
    userid = cursor.fetchone()

    a = filter(str.isalnum, str(userid[0]))
    users =''.join(list(a))

    words=keyword.split(' ')
    search=''
    for i,j in enumerate(words):
        search+="bookname like '%"+str(j)+"%' "
        if i!=len(words)-1:
            search +=" and "
    print("select * from(select * from(select ROW_NUMBER() over(order by mid) as rowid,*from BookData where "+str(search)+")as g where rowid between "+str((int(page)*10)-9)+" and "+str(int(page)*10)+")as q left join users"+str(users) +" on q.mid = users"+str(users)+".mid")
    cursor.execute("select * from(select * from(select ROW_NUMBER() over(order by mid) as rowid,*from BookData where "+str(search)+")as g where rowid between "+str((int(page)*10)-9)+" and "+str(int(page)*10)+")as q left join users"+str(users) +" on q.mid = users"+str(users)+".mid for json auto")
    
    s=''
    while 1:
        row = cursor.fetchone()
        if not row:
            break
        s+=row[0]
    return str(s)

@app.route('/foreignlanguage/')
def foreignlanguaged():
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               "foreignlanguage.json")

@app.route('/popular/')
def popular():
    cursor.execute("select top 6 * from BookData order by likes desc for json auto")
    s=''
    while 1:
        row = cursor.fetchone()
        if not row:
            break
        s+=row[0]
    return str(s)

@app.route('/googlebc02c96297e30e79.html')
def googlesearch():
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               "googlebc02c96297e30e79.html")

@app.route('/newer/')
def newer():
    cursor.execute("select top 6 * from BookData order by ID desc for json auto")
    s=''
    while 1:
        row = cursor.fetchone()
        if not row:
            break
        s+=row[0]
    return str(s)
    

@app.route('/tital/')
def tital():
    
    return send_from_directory(app.config['UPLOAD_FOLDER'],"main_tiatl_list.json")

@app.route('/join/<email>/<password>')
def join(email,password):
    cursor.execute("SELECT * from member where email like '"+str(email)+"' FOR JSON AUTO")
    row = cursor.fetchone() 
    if row:
        return login(email,password)
        
    
    else:
        cursor.execute("select left(newid(),20) AS stringLen")
        newid = cursor.fetchone() 
        cursor.execute("select left(newid(),20) AS stringLen")
        randcode = cursor.fetchone()
        cursor.execute("insert into member values ('"+str(newid[0])+"\',\'"+""+"\',\'"+str(password)+"\',\'"+str(email)+"\',\'"+str(randcode[0])+"\');")
        cnxn.commit()
       
        a = filter(str.isalnum, str(newid[0]))
        tablename =''.join(list(a))

        cursor.execute("create table users"+str(tablename)+"  (mid int null,islike tinyint,store tinyint ,comment ntext null)")
        cnxn.commit()
        cursor.execute("SELECT id,randcode from member where email like '"+str(email)+"' AND password like '"+str(password)+"' FOR JSON AUTO")
        row = cursor.fetchone()
        return str(row[0])


@app.route('/login/<email>/<password>')
def login(email,password):
    cursor.execute("SELECT id,randcode from member where email like '"+str(email)+"' AND password like '"+str(password)+"' FOR JSON AUTO")
    row = cursor.fetchone()
    if not row:
        return "wrong password or email"
    else:
        return str(row[0])

@app.route('/memberdata/<randecode>')
def memberdata(randcode):
    a = filter(str.isalnum, str(randcode))
    tablename =''.join(list(a))
    cursor.execute("SELECT * from users"+str(tablename)+" FOR JSON AUTO")
    row = cursor.fetchone()
    return str(row[0])

@app.route('/likebook/<mid>/<randcode>/<bool>')
def likebook(mid,randcode,bool):
    cursor.execute("SELECT id from member where randcode like '"+str(randcode)+"'")
    userid = cursor.fetchone()
    a = filter(str.isalnum, str(userid[0]))
    users =''.join(list(a))
    cursor.execute("SELECT username from member where randcode like '"+str(randcode)+"' FOR JSON AUTO")
    row = cursor.fetchone()
    if not row:
        return "fail"
    else:
        #a = filter(str.isalnum, str(randcode))
        #users =''.join(list(a))
        if bool=='1':
            cursor.execute("update users"+str(users)+" set islike = 1 where mid = "+str(mid))
            cursor.execute("update BookData set likes += 1 where mid = "+str(mid))
            cnxn.commit()
        if bool=='0':
            cursor.execute("update users"+str(users)+" set islike = 0 where mid = "+str(mid))
            cursor.execute("update BookData set likes -= 1 where mid = "+str(mid))
            cnxn.commit()
        return "ok"

@app.route('/store/<mid>/<randcode>/<bool>')
def store(mid,randcode,bool):
    cursor.execute("SELECT id from member where randcode like '"+str(randcode)+"'")
    userid = cursor.fetchone()

    a = filter(str.isalnum, str(userid[0]))
    users =''.join(list(a))
    cursor.execute("SELECT id from member where randcode like '"+str(randcode)+"' FOR JSON AUTO")
    row = cursor.fetchone()
    if not row:
        return "fail"
    else:
        #a = filter(str.isalnum, str(randcode))
        #users =''.join(list(a))
        if bool=='1':
            cursor.execute("update users"+str(users)+" set store = 1 where mid = "+str(mid))
            cnxn.commit()
        if bool=='0':
            cursor.execute("update users"+str(users)+" set store = 0 where mid = "+str(mid))
            cnxn.commit()
        return "ok"

@app.route('/test/<users>')
def test(users):
    cursor.execute("select BookData.*,users"+str(users)+".islike,users"+str(users)+".comment from users"+str(users)+" Right join BookData ON BookData.mid = users"+str(users)+".mid where bookname like '%資料結構 : 使用Python%' for json auto")

    row = cursor.fetchone() 
    
    return str(row[0])

@app.route('/userlist/<randcode>')
def userlist(randcode):

    cursor.execute("SELECT id from member where randcode like '"+str(randcode)+"' ")
    userid = cursor.fetchone()

    a = filter(str.isalnum, str(userid[0]))
    users =''.join(list(a))
    
    cursor.execute("select BookData.*,users"+str(users)+".islike,users"+str(users)+".comment ,users"+str(users)+".store from BookData Right join users"+str(users)+" ON BookData.mid = users"+str(users)+".mid where store =1 for json auto")
    s=''
    while 1:
        row = cursor.fetchone()
        if not row:
            break
        s+=row[0]
    
    return s


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5000 )
