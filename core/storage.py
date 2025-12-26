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

from imagekitio import ImageKit, ImageKitError
class ImageKitStorage(Storage):
    def __init__(self, IMAGEKIT_PRIVATE_KEY, IMAGEKIT_PUBLIC_KEY, IMAGEKIT_URL_ENDPOINT):
        self.imageKit = ImageKit(
            private_key=IMAGEKIT_PRIVATE_KEY,
            public_key=IMAGEKIT_PUBLIC_KEY,
            url_endpoint=IMAGEKIT_URL_ENDPOINT
        )
    
    def save(self, file_stream, filename, url=""):
        public_url = ""
        if url:
            try:
                upload = self.imageKit.upload_file(
                    file=url,
                    file_name="test-url.jpg",
                    options=UploadFileRequestOptions(
                        response_fields=["is_private_file", "tags"],
                        tags=["tag1", "tag2"]
                    )
                )
                if upload:
                    public_url = upload["url"]
            except ImageKitError as error:
                print(f"ERROR: Error uploading image on imagekit: {error}")
        return public_url
    
    def delete(self, file_identifier):
        return super().delete(file_identifier)
