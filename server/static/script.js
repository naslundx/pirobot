function sendCommand(cmd, cb = null) {
  fetch("/command", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ command: cmd }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (cb) {
        cb(data);
      }
    });
}

function askChatGPT() {
  const query = document.getElementById("query").value;
  fetch("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: query }),
  })
    .then((response) => response.text())
    .then((data) => (document.getElementById("response").innerText = data));
}

function setAI() {
  const query = document.getElementById("aicmd").value;
  sendCommand("goal " + query, (data) => {
    console.log(data);
  });
}

function updateStatus() {
  sendCommand("engine_status", (data) => {
    document.getElementById("engine_status").innerText = data.response;
  });
  sendCommand("ai_status", (data) => {
    document.getElementById("ai_status").innerText = data.response;
  });
}

function connectCameraWebSocket() {
  const socket = new WebSocket(`ws://${window.location.host}/ws/camera`);
  socket.onmessage = (event) => {
    document.getElementById("cameraImage").src =
      "data:image/jpeg;base64," + event.data;
  };
  socket.onclose = () => console.log("Camera WebSocket closed");
  socket.onerror = (err) => console.error("WebSocket error:", err);
}

function onSpeedUpdate() {
  let value = document.getElementById("myRange").value;
  sendCommand(`engine ${value}`);
}

window.onload = function () {
  connectCameraWebSocket();
  setInterval(updateStatus, 1000);
  document.getElementById("myRange").oninput = onSpeedUpdate;
};
