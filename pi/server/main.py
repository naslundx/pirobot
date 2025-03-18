import asyncio
import time
import threading
import RPi.GPIO as GPIO
from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from .ai import AIConnection
from .camera import FrontCamera
from .engine import Engine

# Set environment and HW
load_dotenv()
CAMERA_STREAM_FPS = 2
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
        print('AI command:', command)
        if command is None:
            handle_command('engine 0')
            image_data = camera.capture_as_base64()
            ai.update_towards_goal(image_data)
            continue

        command = command.strip().lower()

        if command == "done":
            handle_command('engine 0')
            ai.is_autonomous = False
        else:
            handle_command(command)
            time.sleep(1.5)

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


@app.websocket("/ws/camera")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        try:
            before = time.time()
            image_data = camera.capture_as_base64()
            await websocket.send_text(image_data)

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
