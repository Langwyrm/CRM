from flask import Flask, render_template, request, redirect, url_for, session
import time
import sqlite3
import rng
from datetime import datetime
import redis
import os
from flask_session import Session

#Connecting to the database
connection = sqlite3.connect("test3.db", check_same_thread=False)

##########################################################################
################################ SUBPROGRAMS #############################
##########################################################################

#Checks whether a number is in a range
def RangeCheck(low,high,num):
    if num >= low and num <= high:
        return True
    else:
        return False
    
def InsertData(database,table,column,value):
    database = database + ".db"
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    connection.commit()
    table = str(table)
    column = str(column)
    value = str(value)
    sql = ("INSERT INTO {0} ({1}) VALUES ('{2}')").format(table,column,value)
    cursor.execute(sql)
    connection.commit()
    

#Gets specific info from a database
def GetInfo(column,condition,infoNeeded,database,table):
    database = database + ".db"
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    connection.commit()
    table = str(table)
    sqlstring = 'SELECT ' + infoNeeded + ' FROM ' + table + ' WHERE ' + column + ' = "' + condition + '"'
    print(sqlstring)
    cursor.execute(sqlstring)
    string = cursor.fetchall()
    if len(string) > 0:
        string = string[0]
    string = str(string)
    number = len(string) - 3
    string = string[2:number]
    return string

#Gets all data from a column from a database
def GetInfoTotal(infoNeeded,database,table):
    database = database + ".db"
    connection = sqlite3.connect(database, check_same_thread=False)
    cursor = connection.cursor()
    connection.commit()
    table = str(table)
    sql = "SELECT " + infoNeeded + " FROM " + table
    cursor.execute(sql)
    stringlist = cursor.fetchall()
    for i in range(len(stringlist)):
        string = stringlist[i]
        string = str(string)
        number = len(string) - 3
        string = string[2:number]
        stringlist[i] = string
    return stringlist

#Gets passwords
def GetPassword(user):
    pwd = GetInfo("Username",user,"Password","test3","test_table")
    return pwd

##########################################################################
##################### SESSION + APP CONFIGURATION ########################
##########################################################################
    
app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', default='*&%^SeCR65876gfdTK£Y')

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url('redis://127.0.0.1:6379')

server_session = Session(app)

##def NoUserToStart():
    #session['signedInUser'] = None
#NoUserToStart()


def checktime():
    now = str(datetime.now())
    nowtime = now.split(" ")
    nowdate = nowtime[0]
    nowtime=nowtime[1]
    return nowdate, nowtime


##########################################################################
################################ PAGES ###################################
##########################################################################

#Page for rerouting already logged in users
@app.route("/loggedin")
def loggedin():
    render_template('loggedin.html', signedInUser=session['signedInUser'])
    time.sleep(3)
    return redirect(url_for('loggedin'))

#Login page
@app.route("/login", methods=['GET', 'POST'])
#Doing login stuff
def login():
    if session['signedInUser'] != None:
        return redirect(url_for('loggedin'))
        time.sleep(3)
        return redirect(url_for('home'))
    render_template('login.html')
    print("Login attempted")
    if request.method == 'POST':
        #while True:
            username = request.form['username']
            password = request.form['password']
            users = GetInfoTotal("Username","test3","test_table")
            if username not in users:
                return redirect(url_for('login'))
            password1 = GetInfo('Username',username,'Password','test3','test_table')
            print(f"Login attempt: Username - {username}, Password - {password}")
            if password1 == password: 
                session['signedInUser'] = username
                #Loading leads for the user
                leads = []
                string = GetInfoTotal(str(session['signedInUser']),"test3","leads")
                for i in range(len(string)):
                    string[i] = string[i].split("|")
                    leads.append(string[i])
                print(leads)
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login'))
    return render_template('login.html')

#Welcome page
@app.route("/")
def welcome():
    if session['signedInUser'] != None:
        return redirect(url_for('home'))
    return render_template('welcome.html')

#Home page
@app.route("/home")
def home():
    if session['signedInUser'] == None:
        return redirect(url_for('welcome'))
    return render_template('home2.html', signedInUser=session['signedInUser'])

#Experimental home page
@app.route("/home2")
def home2():
    return render_template('home.html')

#Signup page
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    cursor = connection.cursor()
    render_template('signup.html')
    print("Signup attempted")
    if request.method == 'POST':
        while True:
            user = request.form['username']
            passwd = request.form['password']
            while True:
                UUIDnum = rng.rng(16)
                if UUIDnum not in GetInfoTotal('UUID', 'test3', 'test_table'):
                    break
            print(f"Signnup attempt: Username - {user}, Password - {passwd}")
            for i in range(len(user)):
                if user[i] == " ":
                    return redirect(url_for('signup'))
            users = GetInfoTotal("Username","test3","test_table")
            if RangeCheck(5,20,len(passwd)) and user not in users:
                cursor.execute("INSERT INTO test_table( Username, Password, UUID,Permissions) VALUES( '" + str(user) + "', '" + str(passwd) + "', '" + str(UUIDnum) + "', 'basic')")
                cursor.execute("ALTER TABLE leads ADD " + user + " TEXT")
                connection.commit()
                return redirect(url_for('login'))
            else:
                return redirect(url_for('signup'))
    return render_template('signup.html')

#Logout page
@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if request.method == 'POST': 
        logout = request.form['logout']
        if logout == "logout":
            session['signedInUser'] = None
            return redirect(url_for('welcome'))
    return render_template('logout.html')

#Admin database editing page
@app.route("/admindata", methods=['GET', 'POST'])
def admindata():
    render_template('admindata.html')
    if request.method == 'POST':
        table = request.form['table']
        column = request.form['column']
        value = request.form['value']
        if session['signedInUser'] != None:
            permission = GetInfo("Username",str(session['signedInUser']),"Permissions","test3","test_table")
        else:
            return redirect(url_for("noperms"))
        if permission == "admin":
            InsertData("test3",table,column,value)
        else:
            return redirect(url_for("noperms"))
    return render_template('admindata.html')

@app.route("/noperms")
def noperms():
    render_template('noperms.html')
    time.sleep(3)
    return redirect(url_for('welcome'))

if __name__ == '__main__':
    app.run(debug=True)