from flask import Flask, request, session, render_template
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
    if username == None:
        return render_template('index.html')
    else:
        return render_template('to_profile.html')

# registration page
@app.route('/register')
def register():
    return render_template('register.html')

# If the username from registration form isn't in use, creates new profile
@app.route('/make_account', methods=['POST'])
def make_account():
    username, password = str(request.form['username']), str(request.form['password'])
    if coll.find_one({'user': username}):
        return render_template('to_register.html')
    else:
        session['username'], session['password'] = username, password
        coll.insert({'user':username, 'password':password})
        return render_template('to_profile.html')

# checks username and password
@app.route('/landing', methods=['POST'])
def landing():
    username, password = str(request.form['username']), str(request.form['password'])
    that_user = coll.find_one({'user': username})
    if that_user:
        if that_user['password'] == password:
            session['username'] = username
            session['password'] = password
            return render_template('to_profile.html')
        else:
            return '''
               <p>Wrong password</p>
               <p><a href='/'>Go back</a></p>
               '''
    else:
        return'''
        <p>No username {}</p>
        <p><a href='/'>Go back</a></p>
        '''.format(username)

# profile page
@app.route('/profile')
def profile():
    username = session.get('username')
    poem_entries = poems_coll.find({'user': username})
    poems = [entry['poem'] for entry in poem_entries]
    return render_template('profile.html', username=username, poems=poems)

# form for writing new poems
@app.route('/write')
def write():
    return render_template('write.html')

# saves a poem from the 'write' form and then redirects to profile
@app.route('/save_poem', methods=['POST'])
def save_poem():
    poem = str(request.form['poem'])
    username = session.get('username')
    poems_coll.insert({'user':username, 'poem':poem})
    return render_template('to_profile.html')

# logs a user out and redirects to index
@app.route('/log_out')
def log_out():
    session.clear()
    return render_template('to_index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
