from os import path
from flask import render_template, request, send_from_directory, jsonify, escape
from app import app
from werkzeug import secure_filename
from style_grader_main import style_grader_driver

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['cpp', 'h'])

# @app.before_request
# def before_request():
#     g.user = current_user

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/',  methods = ['GET'])
@app.route('/index', methods = ['GET', 'POST'])
def index():
    # user = g.user

    if request.method == 'POST':
        # Get the FileStorage instance from request
        file = request.files['file']
        filename = secure_filename(file.filename)
        # Render template with file info
        return render_template('file.html',
            filename = filename,
            type = file.content_type)
    return render_template('index.html',
                            title = 'CSCI 235: Style Checker')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/uploadajax', methods=['POST'])
def add_numbers():
    # Get the name of the uploaded files
    uploaded_files = request.files.getlist("file[]")
    filenames = {}
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(path.join("./app/" + app.config['UPLOAD_FOLDER'], filename))
            filename = path.join("./app/" + app.config['UPLOAD_FOLDER'], filename)
            filenames[filename] = file.filename


    response = style_grader_driver(filenames)

    # HTML-escape the error message responses here before making it json
    for file in response:
        for error in file['errors']:
            error['message'] = escape(error['message'])

    # if response != []:
    #     sub = Submission(user_id = g.user.id, passed_grader = False)
    # else:
    #     sub =  Submission(umich_id = g.user.umich_id, user_id = g.user.id, passed_grader = True)

    # db.session.add(sub)
    # db.session.commit()

    return jsonify(files=response)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

# -------- syllabus -----
@app.route('/syllabus')
def syllabus():
    return render_template('syllabus.html',
                            title = 'CSCI 235: Syllabus')
@app.route('/syllabus.pdf')
def syllabusPDF():
    return app.send_static_file('syllabus.pdf')

# -------- Style Guide -----
@app.route('/style-guide')
def style_guide():
    return render_template('style-guide.html',
                            title = 'CSCI 235: C++ Style Guide')