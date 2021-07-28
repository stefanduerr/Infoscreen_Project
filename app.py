import os
from pathlib import Path
import requests
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from typing import List, Any
from flask_caching import Cache
import json

import trello_auth

config = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)
UPLOAD_FOLDER = '/Users/lukas.schweighofer/PycharmProjects/flaskProjectTV/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'mp4', 'pdf'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
@cache.cached(timeout=50)
def play_video():
    return render_template('player.html')


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
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
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return render_template('upload.html')


@app.route('/uploadvideo', methods=['GET', 'POST'])
def upload_video():
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
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return render_template('upload.html')


@app.route('/uploads/<name>')
def download_file(name):
    filepath = '/Users/lukas.schweighofer/PycharmProjects/flaskProjectTV/static/uploads/' + name
    imagepath = '/Users/lukas.schweighofer/PycharmProjects/flaskProjectTV/static/uploads/slides/' + name
    images: List[any] = convert_from_path(filepath, dpi=200)
    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save(imagepath + str(i) + '.jpg', 'JPEG')
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        name,
    )


@app.route('/uploads/slides', methods=['GET', 'POST'])
def slideshow_static():
    return render_template('slideshow.html')


@app.route('/slides/', methods=['GET', 'POST'])
def slideshow_loop():
    images = os.listdir('/Users/lukas.schweighofer/PycharmProjects/flaskProjectTV/static/uploads/slides/')
    return render_template('slides.html',
                           images=images, )


@app.route('/kpis')
def kpi_dashboard():
    probenforecast_upper = 200000
    probenforecast_lower = 190000
    return render_template('kpi.html',
                           # pass an template
                           probenforecastUpper=probenforecast_upper,
                           probenforecastLower=probenforecast_lower, )


@app.route('/clear/', methods=['GET', 'DELETE'])
def clear_slides():
    mydir = UPLOAD_FOLDER + '/slides'
    filelist = [f for f in os.listdir(mydir) if f.endswith(".jpg")]
    for f in filelist:
        os.remove(os.path.join(mydir, f))
    filelist = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".pdf")]
    for f in filelist:
        os.remove(os.path.join(UPLOAD_FOLDER, f))

    return 'Slides cleared!'
