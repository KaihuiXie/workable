import logging
import os
import bcrypt
from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from werkzeug.utils import secure_filename

# BluePrint setup.
resume_bp = Blueprint('resume', __name__, url_prefix='/resume')

@resume_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file found.'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Ensure the upload directory exists
    upload_folder = "./upload_files"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)  # Create the directory if it does not exist

    # Save the file
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    return jsonify({'message': 'File uploaded successfully'}), 200