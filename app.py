import os
from flask import Flask, flash, request, redirect, url_for, render_template, Response
from werkzeug.utils import secure_filename
from flask_caching import Cache
from pathlib import Path
from forms import LoginForm, RegistrationForm, UploadForm
from flask_sqlalchemy import SQLAlchemy
import csv
import logging
import datetime
from datetime import datetime, date, timedelta
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
import time
from apscheduler.schedulers.background import BackgroundScheduler
import shutil
import sys

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
log2 = logging.getLogger('apscheduler')
log2.setLevel(logging.ERROR)
UPLOAD_FOLDER = Path.cwd().joinpath('static', 'uploads')
UPLOAD_VIDEO = Path.cwd().joinpath('static', 'uploads', 'video')
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
CWD = Path.cwd()
STATIC = Path.cwd().joinpath('static')
ALLOWED_EXTENSIONS = {'mp4'}

config = {
    "SECRET_KEY": "6d8ed540960d1085d183d8e5d236f2da",
    "CACHE_TYPE": 'SimpleCache',  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
    "TEMPLATES_AUTO_RELOAD": True,
    "UPLOAD_FOLDER": UPLOAD_FOLDER,
    "UPLOAD_VIDEO": UPLOAD_VIDEO,
    "SQLALCHEMY_DATABASE_URI": 'sqlite:///site.db',
    "SQLALCHEMY_TRACK_MODIFICATIONS": False
}

app.config.from_mapping(config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    print(User.query.get(int(user_id)), file=sys.stdout)
    return User.query.get(int(user_id))

# User-Klasse für Datenbank
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

# Erstellt Datenbank
init_db()

# File allowed?
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routing zu Seiten
@app.route('/error_test_page', methods=['GET'])
def notFound():
    return render_template('error_test_page.html')

@app.route('/custom_404', methods=['GET'])
def fourohfour():
    return render_template('custom_404.html')

@app.route('/', methods=['GET'])
def default():
    return render_template('default.html')

@app.route('/home')
def home():
    return render_template('index.html')
                        #    sites=get_sites())

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

# Liest Seiten von CSV File (p9,p15,...)
def get_sites():
    # open the file in read mode
    filename = open('C:/Users/stefan.duerr/Documents/flaskProjectTV/sites.csv', 'r')
    # creating dictreader object
    sitesfile = csv.DictReader(filename)

    sites = []

    for col in sitesfile:
        sites.append(col['site'])

    for site in sites:
        if not (os.path.isdir(Path.cwd().joinpath('static', 'uploads', 'video', site))):
            os.mkdir(Path.cwd().joinpath('static', 'uploads', 'video', site))
    return sites

# Routing zu Upload-directory + Upload-Funktion
@app.route('/upload/<folder>', methods=['GET', 'POST'])
@login_required
def upload(folder):
    # folder = "p19"
    form = UploadForm()
    
    if folder == 'p09':
        text = 'Pavillon 9'
    elif folder == 'p15':
        text = 'Pavillon 15'
    elif folder == 'p16':
        text = 'Pavillon 16'
    elif folder == 'p17':
        text = 'Pavillon 17'
    elif folder == 'p18':
        text = 'Pavillon 18'
    elif folder == 'p19':
        text = 'Pavillon 19'

# Wenn Upload-Form korrekt submitted?
    if form.validate_on_submit():
        if form.ifnow.data:
            files = [f for f in os.listdir(Path.cwd().joinpath('static', 'uploads', 'video', folder))
                    if f.endswith(".mp4")]
            for f in files:
                os.remove(Path.cwd().joinpath('static', 'uploads', 'video', folder, f))
            f = form.video.data
            filename = secure_filename(f.filename)
            f.save(Path.cwd().joinpath('static', 'uploads', 'video', folder, filename))
            today = date.today()
            LFname = "Log " + str(today) + ".log"
            cur_dat = datetime.now()
            current_datetime = cur_dat.strftime("%d/%m/%Y %H:%M:%S")
            logging.basicConfig(filename=LFname, level=logging.INFO)
            logging.info(" " + current_datetime + ": " + current_user.username + ' uploaded ' + f.filename + ' on ' + folder + '.')

            return render_template('video_uploaded.html')
        else:
            usertime = str(form.date.data) + ' ' + str(form.time.data)
            usertime_object = datetime.strptime(usertime, '%Y-%m-%d %H:%M:%S')
            
            g = form.video.data
            filename = secure_filename(g.filename)
            g.save(Path.cwd().joinpath('static', 'uploads', 'temp', folder, filename))              
            path = Path.cwd().joinpath('static', 'uploads', 'temp', folder, filename)
            newpath = Path.cwd().joinpath('static', 'uploads', 'video', folder, filename)

            def uploadatgiventime():
                files = [f for f in os.listdir(Path.cwd().joinpath('static', 'uploads', 'video', folder))
                        if f.endswith(".mp4")]
                for f in files:
                    os.remove(Path.cwd().joinpath('static', 'uploads', 'video', folder, f))
                shutil.move(path, newpath)
              
            LFname = "Log " + str(form.date.data) + ".log"
            logging.basicConfig(filename=LFname, level=logging.INFO)
            logging.info(" " + current_user.username + ' scheduled upload of ' + g.filename + ' on ' + folder + ' for ' + str(usertime_object))

            scheduler = BackgroundScheduler()
            scheduler.add_job(func=uploadatgiventime, trigger="date", run_date=usertime_object)

            scheduler.start()
            return render_template('video_uploaded.html')
    else:
        print("unsuccessful")
        
        # flash(form.video.errors)
        
    print(form.errors)

    return render_template('uploadtest.html', form=form, text=text)

@app.route('/uploadvideo/<folder>', methods=['GET', 'POST'])
@login_required
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

# Route zu Register + Register-Funktion
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

# Route zu Login + Login-Funktion
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

# Route, um Videos zu ändern
@app.route("/editscreens")
@login_required
def editscreens():
    return render_template('editscreens.html',
                           sites=get_sites())

@app.route('/time_feed')
def time_feed():
    def generate():
        yield datetime.now().strftime("%Y.%m.%d | %H:%M:%S")  # return also will work
    return Response(generate(), mimetype='text') 

if __name__ == '__main__':
    
    app.run(debug=True)
    
