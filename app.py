import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template, Response
from werkzeug.utils import secure_filename
from flask_caching import Cache
from pathlib import Path
# import forms
from forms import *
from flask_sqlalchemy import SQLAlchemy
import csv
import logging
import datetime
from datetime import datetime, date, timedelta
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
import time
from threading import Thread
from jinja2 import Template
import platform
import subprocess
import sched, time
import ctypes, sys



log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
config = {
    "SECRET_KEY": "6d8ed540960d1085d183d8e5d236f2da",
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
    "TEMPLATES_AUTO_RELOAD": True
}


app.config.from_mapping(config)
cache = Cache(app)
CWD = Path.cwd()
print(CWD)
STATIC = Path.cwd().joinpath('static')
UPLOAD_FOLDER = Path.cwd().joinpath('static', 'uploads')
UPLOAD_VIDEO = Path.cwd().joinpath('static', 'uploads', 'video')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_VIDEO'] = UPLOAD_VIDEO
ALLOWED_EXTENSIONS = {'mp4'}



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    sites = db.relationship('Site', backref='creator', lazy=True)


def __repr__(self):
    return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


def __repr__(self):
    return f"User('{self.username}', '{self.email}', '{self.image_file}')"

def init_db():

    db.create_all()
    # new_user = User(username='testuser212', email='ax@1a.com', password='password')
    # db.session.add(new_user)
    # db.session.commit() 
    # print('test')

init_db()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

loginstatus="true"

@app.route('/error_test_page', methods=['GET'])
def notFound():
    return render_template('error_test_page.html')

@app.route('/', methods=['GET'])
def default():
    return render_template('default.html')

@app.route('/home')
def home():
    return render_template('index.html',
                           sites=get_sites(), state=loginstatus)

@app.route('/stream/<site>', methods=['GET'])
@cache.cached(timeout=50)
def play_video(site):
    videos = os.listdir(Path.cwd().joinpath('static', 'uploads', 'video', site))
    if videos:
        pass
    else:
        site = "fallback"
    return render_template('player.html',
                           site=site,
                           videos=videos)

def get_sites():
    # open the file in read mode
    filename = open('sites.csv', 'r')
    # creating dictreader object
    sitesfile = csv.DictReader(filename)

    sites = []

    for col in sitesfile:
        sites.append(col['site'])

    for site in sites:
        if not (os.path.isdir(Path.cwd().joinpath('static', 'uploads', 'video', site))):
            os.mkdir(Path.cwd().joinpath('static', 'uploads', 'video', site))
    return sites


@app.route('/uploadvideo/<folder>', methods=['GET', 'POST'])
def upload_video(folder):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == ' ':
            flash('No selected file')
            return redirect(request.url)
        files = [f for f in os.listdir(UPLOAD_VIDEO)
                 if f.endswith(".mp4")]
        for f in files:
            os.remove(os.path.join(UPLOAD_VIDEO, f))
        if file and allowed_file(file.filename):
            today = date.today()
            LFname = "Log " + str(today) + ".log"
            cur_dat = datetime.now()
            current_datetime = cur_dat.strftime("%d/%m/%Y %H:%M:%S")
            logging.basicConfig(filename=LFname, level=logging.INFO)
            logging.info(" " + current_datetime + ": " + current_user.username + ' uploaded ' + file.filename + ' on ' + folder + '.')
            filename = secure_filename(file.filename)
            file.save(Path.cwd().joinpath('static', 'uploads', 'video', folder, filename))
            return render_template('video_uploaded.html')
    return render_template('upload.html'), folder


@app.route('/clear/<site>', methods=['GET', 'DELETE'])
#  Route um Videos zu entfernen
def clear_slides(site):
    files = [f for f in os.listdir(Path.cwd().joinpath('static', 'uploads', 'video', site))
             if f.endswith(".mp4")]
    for f in files:
        os.remove(Path.cwd().joinpath('static', 'uploads', 'video', site, f))
    return render_template('deleted.html',
                           site=site)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # print('login sccsf')
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')

@app.route("/editscreens")
@login_required
def editscreens():
    return render_template('editscreens.html',
                           sites=get_sites(), state=loginstatus)

@app.route('/time_feed')
def time_feed():
    def generate():
        yield datetime.now().strftime("%Y.%m.%d | %H:%M:%S")  # return also will work
    return Response(generate(), mimetype='text') 

# ping function, scheitert noch an adminrechten


s = sched.scheduler(time.time, time.sleep)
def ping_daily(sc): 
    ping()
    # do your stuff
    sc.enter(86400, 1, ping_daily, (sc,))

s.enter(5, 1, ping_daily, (s,))

def ping():
    if platform.system() == "Windows":
        print("No Server Environment.")
    else:
        bashCommand = "sudo fping -s -g 10.90.12.1 10.90.12.50"
        
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()





if __name__ == '__main__':
    
    Thread(target = s.run()).start()
    app.run(debug=True)
    
