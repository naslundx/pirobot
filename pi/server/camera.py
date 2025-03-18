from time import sleep
import base64
import io
import time

from picamera2 import Picamera2, Transform


class FrontCamera:
    def __init__(self):
        self._cache = ""
        self._timestamp = 0
        self.CACHE_LIMIT = 500

        self.camera = Picamera2()
        main = {"format": "RGB888", "size": (640, 480), "transform": Transform(vflip=1)}
        config = self.camera.create_still_configuration(main=main)
        self.camera.configure(config)
        self.camera.options["quality"] = 80
        self.camera.start()

        sleep(2)

    def capture_as_base64(self) -> str:
        timestamp = time.time() * 1000
        if timestamp - self._timestamp < self.CACHE_LIMIT:
            return self._cache

        img_bytes = io.BytesIO()
        self.camera.capture_file(img_bytes, format='jpeg')
        img_bytes.seek(0)
        encoded_string = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

        self._cache = encoded_string
        self._timestamp = timestamp

        return encoded_string
