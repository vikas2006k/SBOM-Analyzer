import os
import hashlib
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

class FileHelper:
    """Utility handling secure uploads storage, hashing, and extensions validations."""

    @staticmethod
    def allowed_file(filename, allowed_extensions=None):
        """Check if file extension is valid."""
        if allowed_extensions is None:
            allowed_extensions = {'json', 'csv'}
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @staticmethod
    def calculate_sha256(file_path):
        """Compute the SHA256 checksum of a local file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")

    @staticmethod
    def save_uploaded_file(file_payload, upload_folder=None):
        """Store uploaded file securely with a unique UUID name and return (file_path, checksum)."""
        if not file_payload or file_payload.filename == '':
            raise ValueError("No file payload selected")
        
        if not FileHelper.allowed_file(file_payload.filename):
            raise ValueError("Invalid file extension. Only JSON and CSV are allowed.")

        if upload_folder is None:
            upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")

        os.makedirs(upload_folder, exist_ok=True)
        
        # Split filename to inject unique id
        base_name = secure_filename(file_payload.filename)
        name, ext = os.path.splitext(base_name)
        unique_name = f"{name}_{uuid.uuid4().hex}{ext}"
        destination_path = os.path.join(upload_folder, unique_name)
        
        file_payload.save(destination_path)
        
        # Calculate checksum
        checksum = FileHelper.calculate_sha256(destination_path)
        return destination_path, checksum

