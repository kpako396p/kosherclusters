from flask import Flask, request, render_template, redirect, url_for, session, escape
from flask_restful import Resource, Api, reqparse
import json
from urllib.request import urlopen
import requests
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
import env
import models

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = "lkkajdghdadkglajkgah"

API_URL = env.BaseConfig.API_URL
MANAGE_URL = env.BaseConfig.MANAGE_URL


@app.route("/",methods=['GET'])
def index():
    requestPosts = urlopen(API_URL+'/getposts').read().decode('utf8')
    x = json.loads(requestPosts)
    return render_template('posts.html',
           posts = x)

@app.route("/add", methods=['GET', 'POST'])
def addpost():
    if request.method == 'POST':
        name = request.form.get('name')
        text = request.form.get('text')
        author = request.form.get('author')
        
        def makePost(name, text, author):
            url = (API_URL+'/createpost')
            return requests.post(url, json={
                'name': name,
                'text': text,
                'author': author
                })
        makePost(name, text, author)
        
        return render_template('addpost.html')
    
    else: 
        return render_template('addpost.html')


@app.route('/reg', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        account.Name = request.form.get('username')
        account.Password = request.form.get('password')
        account.Email = request.form.get('email')

        def createUser(username, password, email):
            url = (API_URL+'/registration')
            return requests.post(url, json={
                    'username': account.Name,
                    'password': account.Password,
                    'email': account.Email,
                })
        createUser(account.Name, account.Password, account.Email)
        return redirect('/')
    else:
        return render_template('registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    url = (API_URL+'/login')
    if request.method == 'POST':
        account.Name = request.form.get('username')
        password = request.form.get('password')
        
        def answer(login,password): 
            req = requests.get(url, params={
                'username': login,
                'password': password,
                })
            return (json.loads(req.text))
        
        if answer(account.Name, password)['status'] == 200:
            session['username'] = account.Name
            return redirect('/account')
        elif answer(login, password)['status'] == 403:
            return render_template('login.html',
                status = 'Invalid password. Try again')
        else:
            return render_template('login.html', 
                status = 'User not exist. Try again')
    else:
        return render_template('login.html', status = 'Login, please')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/account', methods=['GET', 'POST'])
def account():
    if request.method == 'GET':
        if 'username' in session:
            url = (MANAGE_URL+'/getnodes')
            req = requests.get(url, params={
                'owner': session['username']
                })
            nodesList = json.loads(req.text)
            print (nodesList)
            return render_template('account.html', username = login, nodes = nodesList)
        else:
            return redirect('/login')
    else:
        return 'POST request not allowed there'

@app.route('/account/pool', methods=['GET', 'POST'])
def pools():
    if request.method == 'GET':
        if 'username' in session:
            return render_template('createpool.html')
        else: 
            return redirect('login')
    else:
        poolName = request.form.get('poolName')

        def createPool(poolname, owner):
            url = (MANAGE_URL+'/createpool')
            return requests.post(url, json={
                'poolName': poolname,
                'poolOwner': owner,
                })
        createPool(poolName, session['username'])
        return  poolName

@app.route('/account/node', methods=['GET', 'POST'])
def nodes():
    if request.method == 'GET':
        if 'username' in session:
            return render_template('createnode.html')
        else: 
            return redirect('login')
    else:
        nodeName = request.form.get('nodeName')
        poolName = request.form.get('poolName')
        
        def createNode(nodename, poolname, owner):
            url = (MANAGE_URL+'/createnode')
            return requests.post(url, json={
                'nodeName': nodename,
                'owner': owner,
                'poolName': poolname,
                })
        createNode(nodeName, poolName, session['username'])
        return redirect('/account')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5001)
