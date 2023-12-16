import os
import zipfile
from flask import Flask, request, jsonify, send_file
from rembg import remove
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

# unique id generator


def generate_unique_filename():
    return str(uuid.uuid4())


@app.route('/rembg', methods=['POST'])
def remove_background():
    # make sure the uploads and outputs folder exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    id = generate_unique_filename()
    CURRENT_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, id)
    os.mkdir(CURRENT_UPLOAD_FOLDER)

    # get the files from post request
    files = request.files.getlist("images")

    # out if no files
    if not files:
        return jsonify({'error': 'No files were uploaded'}), 400

    # read and remove for each file (img)
    for file in files:
        img_data = file.read()
        output_data = remove(img_data)
        filename = file.filename
        output_path = os.path.join(CURRENT_UPLOAD_FOLDER, filename)
        with open(output_path, "wb") as f:
            f.write(output_data)

    # output
    zip_output_dir = os.path.join(
        OUTPUT_FOLDER, "processed_images_" + id + ".zip")
    with zipfile.ZipFile(zip_output_dir, "w") as zip_file:
        for root, _, files in os.walk(CURRENT_UPLOAD_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, file)

    # finally send the output
    return send_file(zip_output_dir)

# catch any other route


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    return 'Not handling this route,sorry %s' % path, 404

 # app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
