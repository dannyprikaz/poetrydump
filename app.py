from flask import Flask, request, session
from flask.ext.session import Session
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import numpy as np
app = Flask(__name__)
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)

client = MongoClient()
db = client.podump
coll = db.users
poems_coll = db.poems

# home page
@app.route('/')
def index():
    username = session.get('username')
    password = session.get('password')
    return '''
    <h1> Welcome to Poetry Dump </h1>
    <form action="/landing" method='POST' >
    <p>
        Username: <input type="text" name="username" value="{}"/>
    </p>
    <p>
        Password: <input type="password" name="password" value="{}"/>
        <input type="submit" />
    </p>
    </form>
    <a href="/register">Register</a>
    '''.format(username, password)

# registration page
@app.route('/register')
def register():
    return '''
    <h1> Register an account: </h1>
    <form action="/make_account" method='POST' >
    <p>
        Username: <input type="text" name="username" />
    </p>
    <p>
        Password: <input type="password" name="password" />
        <input type="submit" />
    </p>
    </form>
    '''

# If the username from registration form isn't in use, creates new profile
@app.route('/make_account', methods=['POST'])
def make_account():
    username, password = str(request.form['username']), str(request.form['password'])
    session['username'], session['password'] = username, password
    if coll.find_one({'username': username}):
        return '''
          <p>The username {} already exists.</p>
           '''.format(username)
    else:
        coll.insert({'user':username, 'password':password})
        return'''
        You are registered.  Return to <a href="/"> homepage</a>.
        '''

# checks username and password
@app.route('/landing', methods=['POST'])
def landing():
    username, password = str(request.form['username']), str(request.form['password'])
    session['username'] = username
    session['password'] = password
    that_user = coll.find_one({'user': username})
    if that_user:
        if that_user['password'] == password:
            return'''
            <script>
            window.location = "/profile"
            </script>
            '''
        else:
            return '''
               <p>Wrong password</p>
               <p><a href='/'>Go back</a></p>
               '''
    else:
        return'''
        No username {}
        '''.format(username)

@app.route('/profile')
def profile():
    username = session.get('username')
    poem_entries = poems_coll.find({'user': username})
    poems = [entry['poem'] for entry in poem_entries]
    return'''
    <h1>Welcome to your profile, {}.</h1>
    <p>Poems go here</p>
    <p>{}</p>
    <p><a href='/write'>Write</a> a new poem.</p>
    '''.format(username, poems)

@app.route('/write')
def write():
    return'''
    <h1>Write a poem</h1>
    <form action="/save_poem" method='POST'>
    <textarea name="poem" rows="30" style="width: 100%"></textarea>
    <input type="submit" />
    </form>
    '''

@app.route('/save_poem', methods=['POST'])
def save_poem():
    poem = str(request.form['poem'])
    username = session.get('username')
    poems_coll.insert({'user':username, 'poem':poem})
    return'''
    <head>
    <script>
    window.location = "/profile"
    </script>
    <head>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
