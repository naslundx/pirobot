import socket
import time
import threading
import os
from pathlib import Path

# import RPi.GPIO as GPIO
from openai import OpenAI
from dotenv import load_dotenv


from .engine import Engine


load_dotenv()
LATEST_IMG_PATH = Path("static/latest.jpg")
SERVER_ADDRESS = ("localhost", int(os.getenv("IO_SOCKET_PORT", 65000)))

engine = Engine()



def handle_command(command):
    if command == "stop":
        engine.stop()
        return "OK"

    if command == "forward":
        engine.forward()
        return "OK"

    if command == "turn_left":
        engine.turn("left")
        return "OK"

    if command == "turn_right":
        engine.turn("right")
        return "OK"

    if command == "reverse":
        engine.reverse()
        return "OK"

    if command == "status":
        return "engines are on"

    #if command == "image_capture":
    #    filename = camera.capture()
    #    return filename

    return "Err"


def hw_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(SERVER_ADDRESS)
    server.listen(5)

    while True:
        conn, addr = server.accept()
        command = conn.recv(1024).decode()
        response = handle_command(command)
        conn.send(response.encode())
        conn.close()


if __name__ == "__main__":
    hw_server()
