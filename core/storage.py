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


from imagekitio import ImageKit
from flask import current_app

class ImageKitStorage(Storage):
    def __init__(self, private_key, public_key, url_endpoint):
        self.imagekit = ImageKit(
            private_key=private_key,
            # public_key=public_key,
            # url_endpoint=url_endpoint
        )

    def save(self, file_stream, filename):
        try:
            upload = self.imagekit.files.upload(
                file=file_stream.read(),   # bytes
                file_name=filename,
                use_unique_file_name=True,
                folder="/profile_pictures"
            )

            # upload is a dict-like object
            return upload.url

        except Exception as e:
            current_app.logger.error(f"ImageKit upload failed: {e}")
            return None

    def delete(self, file_identifier):
        """
        file_identifier = ImageKit fileId (NOT URL)
        """
        return True
        try:
            self.imagekit.delete_file(file_identifier)
            return True
        except Exception as e:
            current_app.logger.error(f"ImageKit delete failed: {e}")
            return False
