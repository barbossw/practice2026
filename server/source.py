from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from objects import WebSocketHandler, InputHandler



@asynccontextmanager
async def lifespan_func(app : FastAPI):
    app.state.web_handler = WebSocketHandler()
    app.state.input_handler = InputHandler()

    yield



app = FastAPI(lifespan = lifespan_func)







@app.get("/")
def root():
    return {"message" : "server root"}


#need to receive data in this format : 
"""{
    "position": {
        "x": 153.2,
        "y": 421.6
    }
}"""

@app.websocket("/ws_connect")
async def websocket_connect(websocket : WebSocket):

    web_handler = websocket.app.state.web_handler
    input_handler = websocket.app.state.input_handler

    accepted = await web_handler.connect(websocket)
    if not accepted:
        return {"message" : "Failed to establish connection - the game is full"}

    try:
        while True:
            data = await websocket.receive_json()
            if websocket is web_handler.player1:
                #process for player 1 here
                input_handler.store_packet(1, data)

            elif websocket is web_handler.player2:
                #process for player 2 here - invert across (0,0)
                data["position"]["x"] *= -1
                data["position"]["y"] *= -1
                input_handler.store_packet(2, data)


    except WebSocketDisconnect:
        web_handler.disconnect(websocket)
