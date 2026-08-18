from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from objects import WebSocketHandler, InputHandler, Master, MatchMaker
from objects import InputPacket, InputPacketType, Position



@asynccontextmanager
async def lifespan_func(app : FastAPI):
    app.state.match_maker = MatchMaker()


    yield



app = FastAPI(lifespan = lifespan_func)







@app.get("/")
def root():
    return {"message" : "server root"}


#expected incoming packets structure (look up class InputPacket):
"""
{
    "type" : "position",
    "data" : {
                "x" : 200,
                "y" : 300
            }
}

or

{
    "type" : "game_mode",
    "data" : {1}
}

"""


@app.websocket("/ws_connect")
async def websocket_connect(websocket : WebSocket):

    match_maker : MatchMaker = app.state.match_maker

    accepted, master = await match_maker.connect(websocket)
    if not accepted:
        return 

    web_handler : WebSocketHandler = master.wsHandler
    input_handler : InputHandler = master.inputHandler

    try:
        while True:
            raw_data = await websocket.receive_json()
    
            raw_packet = input_handler.verify_input_packet(raw_data)  #check if the packet matches the schema
            if (raw_packet is None) or (raw_packet.type is not InputPacketType.POSITION):
                continue

            input_packet = input_handler.verify_position_packet(raw_packet.data) #check if packet data matches the position schema, otherwise dont process it
            if input_packet is None:
                continue
            
            if websocket is web_handler.player1:
                #process for player 1 here
                input_handler.store_packet(1, input_packet)

            elif websocket is web_handler.player2:
                #process for player 2 here - invert across (0,0)
                input_packet_inverted = Position(
                    x= -input_packet.x, 
                    y= -input_packet.y
                    )
                input_handler.store_packet(2, input_packet_inverted)


    except WebSocketDisconnect:
        await web_handler.disconnect(websocket)
    except Exception:
        await web_handler.disconnect(websocket)
        print("Unexpected exception caught")




#test endpoints
@app.get("/check_connections")
async def check_connections():
    master : Master = app.state.master
    web_handler : WebSocketHandler = master.wsHandler
    player1_connected = False
    player2_connected = False
    if web_handler.player1 is not None:
        player1_connected = True
    if web_handler.player2 is not None:
        player2_connected = True

    return {
        "number_of_connected_players" : web_handler.number_of_connected_players(),
        "player1_connected" : player1_connected,
        "player2_connected" : player2_connected
    }
        

@app.get("/check_inputHandler")
async def check_inputHandler():
    master : Master = app.state.master
    input_handler : InputHandler = master.inputHandler

    return {
        "get_last_packets(1)" : input_handler.get_last_packets(1),
        "get_last_packets(2)" : input_handler.get_last_packets(2)
    }