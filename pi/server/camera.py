from pathlib import Path
from time import sleep
import os

from picamera2 import Picamera2


class FrontCamera:
    def __init__(self):
        # https://chatgpt.com/c/67cb5a21-83ac-8006-bb95-93e5f6bb3bb0
        self.camera = Picamera2()
        config = self.camera.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
        self.camera.configure(config)
        self.camera.start()
        self.path = Path(os.environ['HOME'])
        sleep(2)

    def capture(self, filename="latest"):
        path = self.path / f"{filename}.jpg"
        self.camera.take_photo(path)
        return str(path)
