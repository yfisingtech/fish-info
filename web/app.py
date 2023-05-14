from flask import Flask, render_template, request, session
from flask_session import Session
from werkzeug.utils import secure_filename
from photo_analyzer import analyze_photo
from flask import send_from_directory
import os
import tempfile
import shutil
import time

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = tempfile.mkdtemp()
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 300  # セッションの有効期限を300秒に設定

Session(app)

def create_temp_folder():
    temp_folder = tempfile.mkdtemp()
    return temp_folder

def remove_temp_folder(temp_folder):
    shutil.rmtree(temp_folder)

@app.before_request
def check_session_timeout():
    if 'temp_folder' in session and 'session_expires' in session:
        if time.time() > session['session_expires']:
            remove_temp_folder(session['temp_folder'])
            session.clear()

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        if 'photo' in request.files:
            # Create temporary folder for the current session
            session['temp_folder'] = create_temp_folder()
            photo = request.files['photo']
            filename = secure_filename(photo.filename)
            session['img_file']=filename

            # Save file to the temporary folder

            photo.save(os.path.join(session['temp_folder'], session['img_file']))
            # Set session expiration time
            session['session_expires'] = time.time() + app.config['PERMANENT_SESSION_LIFETIME']
            result = analyze_photo()
            return render_template('index.html', result=result)

    return render_template('index.html')

@app.route('/uploaded_image/<string:image_name>')
def uploaded_image(image_name):
    return send_from_directory(session['temp_folder'], image_name)


if __name__ == '__main__':
    app.run()
