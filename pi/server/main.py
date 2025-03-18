import os
import base64
import asyncio
import time
import threading
import RPi.GPIO as GPIO
from pathlib import Path
from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from .ai import AIConnection
from .camera import FrontCamera
from .engine import Engine

# Load environment variables
load_dotenv()
HOME_DIR = Path(os.environ['HOME'])
LATEST_IMG_PATH = HOME_DIR / "latest.jpg"
CAMERA_STREAM_FPS = 2

# HW interface
GPIO.setmode(GPIO.BCM)
camera = FrontCamera()
engine = Engine()
ai = AIConnection()

# Server
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# AI
def background_task():
    while True:
        if not ai.is_autonomous:
            time.sleep(3)
            continue

        command = ai.get_next_command()
        if command is None:
            ai.update_towards_goal(LATEST_IMG_PATH)

        elif command == "done":
            ai.is_autonomous = False

        else:
            handle_command(command)
            time.sleep(2)

thread = threading.Thread(target=background_task, daemon=True)
thread.start()


class CommandRequest(BaseModel):
    command: str


def handle_command(command):
    if command == "stop":
        ai.is_autonomous = False
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

    if command == "engine_status":
        return engine.status

    if command == "ai_status":
        return ai.status

    if command.startswith("goal "):
        goal = command[5:].strip()
        ai.set_goal(goal)
        ai.is_autonomous = True

    if command.startswith("engine "):
        speed = int(command.split(" ")[1])
        if 0 <= speed <= 100:
            engine.setSpeed(speed // 4)
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
    data = await request.json()
    user_input = data.get("query", "")
    response = ai.get_response(user_input)
    return response
