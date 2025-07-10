from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

# Example bot state
bots = [
    {
        "id": 1,
        "x": 0, "y": 0, "z": 0,
        "status": "idle",
        "assigned_order_id": None,
        "destination_bin": None,
        "path": []
    }
]
GRID_SIZE = (6, 6, 6)

def astar_3d(start, goal):
    # Dummy straight-line path for demo; replace with real A* logic
    path = []
    for i in range(7):
        x = int(start[0] + (goal[0] - start[0]) * i / 6)
        y = int(start[1] + (goal[1] - start[1]) * i / 6)
        z = int(start[2] + (goal[2] - start[2]) * i / 6)
        path.append((x, y, z))
    return path

@app.get("/bots")
def get_bots():
    return bots

@app.websocket("/ws/bots")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Move bot along its path
        for bot in bots:
            if bot["path"]:
                bot["x"], bot["y"], bot["z"] = bot["path"].pop(0)
                bot["status"] = "moving"
            else:
                bot["status"] = "idle"
        await websocket.send_json(bots)
        await asyncio.sleep(0.5)

@app.post("/assign_path/")
async def assign_path(bot_id: int, goal_x: int, goal_y: int, goal_z: int, order_id: int = None, destination_bin: str = None):
    for bot in bots:
        if bot["id"] == bot_id:
            bot["path"] = astar_3d((bot["x"], bot["y"], bot["z"]), (goal_x, goal_y, goal_z))
            bot["status"] = "assigned"
            bot["assigned_order_id"] = order_id
            bot["destination_bin"] = destination_bin
    return {"success": True} 