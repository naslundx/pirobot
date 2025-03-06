import socket
import time
import threading
import os
from pathlib import Path

# import RPi.GPIO as GPIO
from openai import OpenAI
from dotenv import load_dotenv

from .engine import Engine


# client = OpenAI()
load_dotenv()
LATEST_IMG_PATH = Path("static/latest.jpg")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERVER_ADDRESS = ("localhost", int(os.getenv("IO_SOCKET_PORT", 65000)))

# Robot I/O
engine = Engine()

def capture_image():
    import cv2

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(LATEST_IMG_PATH, frame)

    cap.release()


def interpret_image():
    with open(LATEST_IMG_PATH, "rb") as image_file:
        image_data = image_file.read()

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        api_key=OPENAI_API_KEY,
        messages=[{"role": "user", "content": "What is in this image?"}],
        files=[{
            "name": "image.jpg",
            "type": "image/jpeg",
            "data": image_data
        }]
    )

    return response.choices[0].message.content


def handle_command(command):
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
        return { "engine": engine.status }

    return "Err"


def hw_server():
    print("hello")

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
