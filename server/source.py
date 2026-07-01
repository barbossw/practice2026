from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


@app.get("/")
def root():
    return {"message" : "server root"}



@app.websocket("/ws_connect")
async def websocket_connect(websocket : WebSocket):
    await websocket.accept()