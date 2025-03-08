from pathlib import Path
import os

import picamzero


class FrontCamera:
    def __init__(self):
        # https://chatgpt.com/c/67cb5a21-83ac-8006-bb95-93e5f6bb3bb0
        self.cam = picamzero.Camera()

        home_dir = os.environ['HOME']
        self.path = Path(home_dir)

    def capture(self, filename="latest"):
        path = self.path / f"{filename}.jpg"
        self.cam.take_photo(path)
        return str(path)
