import abc
class Storage(abc.ABC):
    @abc.abstractmethod
    def save(self, file_stream: bytearray, filename: str):
        """Store file and return its url"""
        pass
    @abc.abstractmethod
    def delete(self, file_identifier: str):
        """delete file with given file identifier id/link"""
        pass

import os
from werkzeug.utils import secure_filename
from flask import current_app

class LocalStorage(Storage):
    # NOTE: Static/upload must exists
    def __init__(self, upload_dir="static\\upload"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def save(self, file_stream, filename):
        filename = secure_filename(filename)
        path = os.path.join(current_app.root_path, self.upload_dir, filename)
        file_stream.save(path)
        public_url = f"/{self.upload_dir}/{filename}".replace("\\", "/")
        return public_url
    
    def delete(self, file_identifier):
        # NOTE: need to verify the correct file path otherwise user can delete anything from file path
        if os.path.exists(file_identifier):
            os.remove(file_identifier)
