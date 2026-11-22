import datetime
from fastapi import FastAPI, Request, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, PlainTextResponse
import uvicorn

app = FastAPI(title="ARIS // NEXUS")
VERIFY_TOKEN = "ARIS_NEXUS_2026"
SECRET_PIN = "2026"
YOUTUBE_DECOY_URL = "https://www.youtube.com/results?search_query=class+11+physics+thermodynamics+one+shot"

connected_clients: list[WebSocket] = []
event_log: list[dict] = []
event_counter = 0

HUD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <meta name="theme-color" content="#04070d" />
  <title>Class 11 Physics Notes</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; -webkit-tap-highlight-color: transparent; }
    body {
      background: #04070d; color: #e2e8f0; min-height: 100dvh;
      display: flex; flex-direction: column; align-items: center; padding: 16px;
    }
    .container { width: 100%; max-width: 720px; }
    .hidden { display: none !important; }

    .decoy-box {
      background: #0b1120; border: 1px solid #1e293b; border-radius: 18px;
      padding: 24px 20px; margin-top: 12px;
    }
    .decoy-box h2 { color: #38bdf8; font-size: clamp(18px, 4vw, 22px); margin-bottom: 10px; }
    .formula {
      background: #050914; padding: 14px; border-radius: 10px;
      font-family: monospace; color: #a5f3fc; margin: 10px 0; font-size: 14px;
      border-left: 3px solid #0284c7;
    }
    .pin-row { display: flex; gap: 10px; margin-top: 20px; }
    .pin-row input {
      flex: 1; padding: 14px; border-radius: 10px; border: 1px solid #334155;
      background: #020617; color: #fff; text-align: center; letter-spacing: 8px;
      font-size: 18px; min-width: 0;
    }
    .pin-row button {
      padding: 0 22px; border-radius: 10px; border: none;
      background: #38bdf8; color: #04070d; font-weight: 800; font-size: 14px; cursor: pointer;
    }

    header {
      display: flex; justify-content: space-between; align-items: center;
      padding: 14px 18px; background: #0b1120; border: 1px solid #1e293b;
      border-radius: 14px; margin-bottom: 16px; gap: 10px;
    }
    .title { font-weight: 800; letter-spacing: 1.5px; font-size: clamp(14px, 3.5vw, 17px); color: #38bdf8; }
    .badge {
      font-size: 11px; padding: 5px 10px; border-radius: 999px; white-space: nowrap;
      background: rgba(16, 185, 129, 0.15); color: #34d399; font-weight: 700;
    }
    .alert-banner {
      background: linear-gradient(135deg, rgba(14, 165, 233, 0.16), rgba(168, 85, 247, 0.16));
      border: 1px solid #38bdf8; border-radius: 16px; padding: 26px 18px;
      text-align: center; margin-bottom: 16px; transition: 0.25s;
    }
    .alert-banner.active {
      box-shadow: 0 0 35px rgba(56, 189, 248, 0.5);
      transform: scale(1.01);
    }
    .protocol-text { font-size: clamp(20px, 5vw, 26px); font-weight: 800; color: #ffffff; letter-spacing: 0.5px; }
    .sub-text { font-size: 12px; color: #94a3b8; margin-top: 6px; letter-spacing: 1px; }

    .controls {
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 16px;
    }
    @media (max-width: 520px) {
      .controls { grid-template-columns: 1fr; }
    }
    .controls button {
      padding: 15px 12px; border-radius: 12px; border: none; cursor: pointer;
      font-weight: 800; font-size: 13px; letter-spacing: 0.5px; transition: transform 0.1s;
    }
    .controls button:active { transform: scale(0.97); }
    .btn-panic { background: #ef4444; color: #fff; box-shadow: 0 4px 14px rgba(239, 68, 68, 0.35); }
    .btn-perm { background: #1e293b; color: #e2e8f0; border: 1px solid #334155; }
    .btn-test { background: #38bdf8; color: #04070d; }

    .hint-bar {
      text-align: center; font-size: 11px; color: #64748b; margin-bottom: 14px;
    }
    .feed {
      background: #0b1120; border: 1px solid #1e293b; border-radius: 14px; padding: 16px;
    }
    .feed h3 { font-size: 12px; color: #94a3b8; letter-spacing: 1.5px; margin-bottom: 12px; }
    .log-item {
      padding: 12px 14px; background: #050914; border-left: 3px solid #38bdf8;
      border-radius: 8px; margin-bottom: 8px; display: flex; justify-content: space-between;
      align-items: center; font-size: 13px; gap: 8px;
    }
    .time { color: #64748b; font-size: 11px; font-family: monospace; white-space: nowrap; }
  </style>
</head>
<body>
  <div class="container">
    <div id="decoyScreen" class="decoy-box">
      <h2>Class 11 Physics — Thermodynamics Revision</h2>
      <p style="color:#94a3b8; font-size:14px;">First Law of Thermodynamics & Carnot Cycle Efficiency:</p>
      <div class="formula">ΔQ = ΔU + ΔW &nbsp;|&nbsp; η = 1 - (T₂ / T₁)</div>
      <div class="formula">PV^γ = Constant &nbsp;|&nbsp; Cp - Cv = R</div>
      <div class="pin-row">
        <input type="password" id="pinInput" inputmode="numeric" maxlength="6" placeholder="••••" />
        <button onclick="unlockHud()">OPEN</button>
      </div>
    </div>

    <div id="nexusScreen" class="hidden">
      <header>
        <div class="title">◈ ARIS // NEXUS</div>
        <div class="badge" id="connStatus">● ONLINE</div>
      </header>

      <div class="alert-banner" id="banner">
        <div class="protocol-text" id="protocolText">STEALTH SHIELD ACTIVE</div>
        <div class="sub-text" id="protocolSub">CROSS-DEVICE RELAY ARMED</div>
      </div>

      <div class="controls">
        <button class="btn-panic" onclick="triggerPanicYouTube()">🚨 ESCAPE → YOUTUBE</button>
        <button class="btn-perm" onclick="enableAlerts()">🔔 ENABLE ALERTS</button>
        <button class="btn-test" onclick="testTrigger()">⚡ TEST PING</button>
      </div>

      <div class="hint-bar">
        Desktop: Press <b>ESC</b> &nbsp;|&nbsp; Mobile: Tap <b>ESCAPE</b> or <b>Two-Finger Tap</b> anywhere
      </div>

      <div class="feed">
        <h3>STEALTH TELEMETRY LOG</h3>
        <div id="logList"></div>
      </div>
    </div>
  </div>

  <script>
    const SECRET_PIN = "__SECRET_PIN__";
    const YOUTUBE_URL = "__YOUTUBE_URL__";
    const decoyScreen = document.getElementById("decoyScreen");
    const nexusScreen = document.getElementById("nexusScreen");
    const pinInput = document.getElementById("pinInput");
    const statusEl = document.getElementById("connStatus");
    const banner = document.getElementById("banner");
    const textEl = document.getElementById("protocolText");
    const subEl = document.getElementById("protocolSub");
    const logList = document.getElementById("logList");

    let lastSeenCount = -1;

    function setBadgeOnline(online) {
      if (online) {
        statusEl.textContent = "● ONLINE";
        statusEl.style.color = "#34d399";
        statusEl.style.background = "rgba(16, 185, 129, 0.15)";
      } else {
        statusEl.textContent = "● RETRYING";
        statusEl.style.color = "#fbbf24";
        statusEl.style.background = "rgba(251, 191, 36, 0.15)";
      }
    }

    function unlockHud() {
      if (pinInput.value === SECRET_PIN) {
        decoyScreen.classList.add("hidden");
        nexusScreen.classList.remove("hidden");
        pinInput.value = "";
        syncState();
      } else {
        pinInput.value = "";
      }
    }

    function triggerAlertUI(item) {
      textEl.textContent = item.message;
      subEl.textContent = `ENCRYPTED SIGNAL • ${item.time}`;
      banner.classList.add("active");
      setTimeout(() => banner.classList.remove("active"), 4000);

      if (navigator.vibrate) navigator.vibrate([120, 60, 120]);
      if (Notification.permission === "granted") {
        new Notification("System Telemetry", { body: item.message });
      }
    }

    async function syncState() {
      try {
        const res = await fetch("/api/status", { cache: "no-store" });
        if (!res.ok) throw new Error("Sync failed");
        const data = await res.json();
        setBadgeOnline(true);

        if (lastSeenCount === -1) {
          lastSeenCount = data.count;
          logList.innerHTML = "";
          data.logs.forEach(addLogRow);
        } else if (data.count > lastSeenCount) {
          lastSeenCount = data.count;
          logList.innerHTML = "";
          data.logs.forEach(addLogRow);
          if (data.logs.length > 0) {
            triggerAlertUI(data.logs[data.logs.length - 1]);
          }
        }
      } catch (err) {
        setBadgeOnline(false);
      }
    }

    setInterval(syncState, 2000);
    syncState();

    function connectSocket() {
      try {
        const proto = location.protocol === "https:" ? "wss:" : "ws:";
        const ws = new WebSocket(`${proto}//${location.host}/ws/nexus`);
        ws.onopen = () => setBadgeOnline(true);
        ws.onmessage = () => syncState();
        ws.onclose = () => setTimeout(connectSocket, 4000);
      } catch (e) {}
    }
    connectSocket();

    function triggerPanicYouTube() {
      fetch("http://127.0.0.1:48912/panic", { method: "POST" }).catch(() => {});
      window.location.replace(YOUTUBE_URL);
    }

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") triggerPanicYouTube();
      if (e.key === "Enter" && !decoyScreen.classList.contains("hidden")) unlockHud();
    });

    document.addEventListener("touchstart", (e) => {
      if (e.touches.length >= 2 && !nexusScreen.classList.contains("hidden")) {
        triggerPanicYouTube();
      }
    });

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        nexusScreen.classList.add("hidden");
        decoyScreen.classList.remove("hidden");
      } else {
        syncState();
      }
    });

    function addLogRow(item) {
      const div = document.createElement("div");
      div.className = "log-item";
      div.innerHTML = `<span><strong>${item.message}</strong></span><span class="time">${item.time}</span>`;
      logList.prepend(div);
    }

    function enableAlerts() {
      Notification.requestPermission();
    }

    function testTrigger() {
      fetch("/bridge/trigger", { method: "POST" }).then(() => syncState());
    }
  </script>
</body>
</html>
""".replace("__SECRET_PIN__", SECRET_PIN).replace("__YOUTUBE_URL__", YOUTUBE_DECOY_URL)

async def dispatch_protocol(source: str):
    global event_counter
    event_counter += 1
    now = datetime.datetime.now().strftime("%I:%M:%S %p")
    payload = {
        "type": "ALERT",
        "message": "Starting protocols, Boss.",
        "source": source,
        "time": now
    }
    event_log.append(payload)
    if len(event_log) > 20:
        event_log.pop(0)

    for ws in list(connected_clients):
        try:
            await ws.send_json(payload)
        except Exception:
            connected_clients.remove(ws)

@app.get("/", response_class=HTMLResponse)
async def hud_interface():
    return HUD_HTML

@app.get("/api/status")
async def get_status():
    return {"status": "online", "count": event_counter, "logs": event_log}

@app.get("/insta-webhook")
async def verify_insta(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    return PlainTextResponse(content="Forbidden", status_code=403)

@app.post("/insta-webhook")
async def insta_webhook(request: Request):
    data = await request.json()
    if data.get("object") == "instagram":
        await dispatch_protocol("STEALTH_NODE")
    return {"status": "ok"}

@app.post("/bridge/trigger")
async def bridge_trigger():
    await dispatch_protocol("STEALTH_NODE")
    return {"status": "delivered", "message": "Starting protocols, Boss."}

@app.websocket("/ws/nexus")
async def nexus_ws(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        if ws in connected_clients:
            connected_clients.remove(ws)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
