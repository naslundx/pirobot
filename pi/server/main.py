import os
import json
import socket
import base64
import asyncio
import websockets
from pathlib import Path
from fastapi import FastAPI, WebSocket, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

from .camera import FrontCamera

camera = FrontCamera()

# client = OpenAI()

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
IO_SOCKET = ("localhost", int(os.getenv("IO_SOCKET_PORT", 65000)))
HOME_DIR = os.environ['HOME']
LATEST_IMG_PATH = Path(HOME_DIR) / "latest.jpg"


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


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


class CommandRequest(BaseModel):
    command: str


async def send_to_io(command: str):
    try:
        reader, writer = await asyncio.open_connection(*IO_SOCKET)
        writer.write(command.encode())
        await writer.drain()
        response = await reader.read(1024)
        writer.close()
        await writer.wait_closed()
        return response.decode()
    except Exception as e:
        return f"Error communicating with IO: {e}"


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("static/index.html", "r") as file:
        return file.read()


@app.post("/command")
async def send_command(request: CommandRequest):
    response = await send_to_io(request.command.strip())
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
            camera.capture()

            with open(LATEST_IMG_PATH, "rb") as image_file:
                image_data = image_file.read()
                encoded_data = base64.b64encode(image_data).decode("utf-8")
                await websocket.send_text(encoded_data)

            # TODO Adapt waiting time
            await asyncio.sleep(1)

        except Exception:
            break


@app.post("/ask")
async def ask_chatgpt(request: Request):
    try:
        data = await request.json()
        user_input = data.get("query", "")

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_input}],
            api_key=OPENAI_API_KEY
        )

        return response.choices[0].message.content

    except:
        return "N/A"
