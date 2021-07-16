import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from typing import List, Any


app = Flask(__name__)
FLASK_ENV = 'development'
UPLOAD_FOLDER = '/Users/lukas.schweighofer/PycharmProjects/flaskProject/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
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
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return render_template('upload.html')


@app.route('/uploads/<name>')
def download_file(name):
    filepath = '/Users/lukas.schweighofer/PycharmProjects/flaskProject/static/uploads/' + name
    imagepath = '/Users/lukas.schweighofer/PycharmProjects/flaskProject/static/uploads/slides/converted'
    images: List[any] = convert_from_path(filepath, dpi=200)
    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save(imagepath + str(i) + '.jpg', 'JPEG')
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        name,
    )


@app.route('/uploads/slides', methods=['GET', 'POST'])
def slideshow():
    images = os.listdir('/Users/lukas.schweighofer/PycharmProjects/flaskProject/static/uploads/slides/')
    return render_template('slideshow.html')




