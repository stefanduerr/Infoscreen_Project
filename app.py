import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from flask_caching import Cache
from pathlib import Path
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
import csv

app = Flask(__name__)
config = {
    "SECRET_KEY": "6d8ed540960d1085d183d8e5d236f2da",
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html',
                           sites=get_sites())


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
            filename = secure_filename(file.filename)
            file.save(Path.cwd().joinpath('static', 'uploads', 'video', folder, filename))
            return render_template('video_uploaded.html')
    return render_template('upload.html')


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
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)
