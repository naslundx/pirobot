import os
import json
import socket
import base64
import asyncio
import websockets
import time
import RPi.GPIO as GPIO
from pathlib import Path
from fastapi import FastAPI, WebSocket, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from .ai import AIConnection
from .camera import FrontCamera
from .engine import Engine

# Load environment variables
load_dotenv()
HOME_DIR = os.environ['HOME']
LATEST_IMG_PATH = Path(HOME_DIR) / "latest.jpg"
CAMERA_STREAM_FPS = 2

# HW interface
GPIO.setmode(GPIO.BCM)
camera = FrontCamera()
engine = Engine()
ai = AIConnection()

# Server
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class CommandRequest(BaseModel):
    command: str


def handle_command(command):
    if command == "stop":
        engine.stop()
        return "OK"

    if command == "forward":
        engine.forward()
        return "OK"

    if command == "turn_left":
        engine.turnLeft()
        return "OK"

    if command == "turn_right":
        engine.turnRight()
        return "OK"

    if command == "reverse":
        engine.reverse()
        return "OK"

    if command == "status":
        return engine.status

    if command.startswith("engine "):
        speed = int(command.split(" ")[1])
        if 0 <= speed <= 100:
            engine.setSpeed(speed);
        return "OK"

    return "Err"


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("static/index.html", "r") as file:
        return file.read()


@app.post("/command")
async def send_command(request: CommandRequest):
    try:
        response = handle_command(request.command.strip())
    except Exception:
        response = "Error"

    return {"response": response}


@app.get("/image")
async def get_latest_image():
    if LATEST_IMG_PATH.exists():
        return FileResponse(LATEST_IMG_PATH)

    return None


@app.websocket("/ws/camera")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        try:
            before = time.time()
            camera.capture()

            with open(LATEST_IMG_PATH, "rb") as image_file:
                image_data = image_file.read()
                encoded_data = base64.b64encode(image_data).decode("utf-8")
                await websocket.send_text(encoded_data)

            duration = time.time() - before
            if duration < (1 / CAMERA_STREAM_FPS):
                await asyncio.sleep((1 / CAMERA_STREAM_FPS) - duration)

        except Exception as e:
            print(e)
            await asyncio.sleep(5)


@app.post("/ask")
async def ask_chatgpt(request: Request):
    try:
        data = await request.json()
        user_input = data.get("query", "")
        response = ai.get_response(user_input)
        return response

    except:
        return "N/A"
