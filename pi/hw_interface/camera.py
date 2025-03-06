from pathlib import Path
import os

import picamzero


class FrontCamera:
    def __init__(self):
        self.cam = picamzero.Camera()

        home_dir = os.environ['HOME']
        self.path = Path(home_dir)

    def capture(self, filename="latest"):
        path = self.path / f"{filename}.jpg"
        self.cam.start_preview()
        self.cam.take_photo(path)
        self.cam.stop_preview()
        return str(path)
