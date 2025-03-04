import socket
import time
import threading
import os
from pathlib import Path

import RPi.GPIO as GPIO
from openai import OpenAI
from dotenv import load_dotenv


# client = OpenAI()
load_dotenv()
LATEST_IMG_PATH = Path("static/latest.jpg")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERVER_ADDRESS = ("localhost", int(os.getenv("IO_SOCKET_PORT", 65000)))

# Robot I/O
PIN_MOTOR1_SPEED = 12
PIN_MOTOR1_DIRECTION = 26
PIN_MOTOR2_SPEED = 13
PIN_MOTOR2_DIRECTION = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_MOTOR1_SPEED, GPIO.OUT)
GPIO.setup(PIN_MOTOR2_SPEED, GPIO.OUT)
GPIO.setup(PIN_MOTOR1_DIRECTION, GPIO.OUT)
GPIO.setup(PIN_MOTOR2_DIRECTION, GPIO.OUT)
MOTOR_1 = GPIO.PWM(PIN_MOTOR1_SPEED, 1000)
MOTOR_2 = GPIO.PWM(PIN_MOTOR2_SPEED, 1000)


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
        MOTOR_1.start(20)
        MOTOR_2.start(20)
        return "OK"
    elif command == "stop":
        MOTOR_1.stop()
        MOTOR_2.stop()
        return "OK"
    elif command == "status":
        return "Motors: Running, Battery: 85%"
    # elif command == "capture":
    #     capture_image()
    #     return "Image captured."
    # elif command == "interpret":
    #     return interpret_image()
    else:
        return "Unknown command."

def io_server():
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
    io_server()
