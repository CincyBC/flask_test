import os

from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
from run import run_script

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return "<h1>DataKind</h1><br><h2>Partning with United Way</h2>", 200 


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_location = os.path.join('input', filename)
            file.save(save_location)

            output_file = run_script(save_location)
            return redirect(url_for('download'))

    return render_template('upload.html')

@app.route('/download')
def download():
    return render_template('download.html', files=os.listdir('run/model_scoring'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('run/model_scoring', filename)

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500
