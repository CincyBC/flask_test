import os
import yaml
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, Response, flash
from werkzeug.utils import secure_filename
from datetime import datetime
from run import run_script
from time import sleep
from loguru import logger

app = Flask(__name__)

app.secret_key = "secret key"

ALLOWED_EXTENSIONS = set(['csv'])
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# configure logger
logger.add("run/job.log", format="{time} - {message}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # if 'files[]' not in request.files:
        #     flash('No file part')
        #     return redirect(request.url)

        files = request.files.getlist('files[]')
        logger.info(files)

        for file in files:
            logger.info(file)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                logger.info(f"File Saved: {filename}")

        # flash('File(s) successfully uploaded')
        # run_script(os.path.join(UPLOAD_FOLDER))
        return redirect(url_for('download'))

    return render_template('index.html'), 200 


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            logger.info(file.filename)
            filename = secure_filename(file.filename)
            save_location = os.path.join(UPLOAD_FOLDER, filename)
            logger.info(save_location)
            file.save(save_location)

            output_file = run_script(save_location)
            # return send_from_directory('run/model_scoring', '')
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

# adjusted flask_logger
def flask_logger():
    """creates logging information"""
    open("run/job.log", 'w').close()
    with open("run/job.log") as log_info:
        for i in range(10000):
            data = log_info.read()
            yield data.encode()
            sleep(1)

@app.route("/log_stream", methods=["GET"])
def stream():
    """returns logging information"""
    return Response(flask_logger(), mimetype="text/plain", content_type="text/event-stream")

if __name__ == "__main__":
    # Create empty job.log, old logging will be deleted
    
    app.run(host="0.0.0.0", port=5000, threaded=True, static_folder="static/")