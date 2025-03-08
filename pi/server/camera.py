from pathlib import Path
from time import sleep
import os

from picamera2 import Picamera2


class FrontCamera:
    def __init__(self):
        self.camera = Picamera2()
        config = self.camera.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
        self.camera.configure(config)
        self.camera.start()
        self.path = Path(os.environ['HOME'])
        sleep(2)

    def capture(self, filename="latest"):
        path = self.path / f"{filename}.jpg"
        self.camera.capture_file(path)
        return str(path)
