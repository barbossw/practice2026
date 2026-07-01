from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from objects import WebSocketHandler



@asynccontextmanager
async def lifespan_func(app : FastAPI):
    app.state.web_handler = WebSocketHandler()

    yield



app = FastAPI(lifespan = lifespan_func)







@app.get("/")
def root():
    return {"message" : "server root"}



@app.websocket("/ws_connect")
async def websocket_connect(websocket : WebSocket):

    handler = websocket.app.state.web_handler
    accepted = await handler.connect(websocket)
    if not accepted:
        return {"message" : "Failed to establish connection - the game is full"}

    try:
        while True:
            data = await websocket.receive_text()
            if websocket is handler.player1:
                #process for player 1 here
                pass
            elif websocket is handler.player2:
                #process for player 2 here - invert across (0,0)
                pass
    except WebSocketDisconnect:
        handler.disconnect(websocket)