from dataclasses import dataclass
from typing import overload
from fastapi import WebSocket, WebSocketDisconnect
from enum import IntEnum
from constants import *
from collections import deque
import math
import asyncio
from source import app

@dataclass
class Pair:
    first : float
    second : float

    @overload
    def __mul__(self, other: "Pair") -> float: ...

    @overload
    def __mul__(self, other: float) -> "Pair": ...

    @overload
    def __mul__(self, other: int) -> "Pair": ...

    def __mul__(self, other):
        if isinstance(other, Pair):
              return self.first * other.first + self.second * other.second
        elif isinstance(other, (int, float)):
             return Pair(
                  self.first * other,
                  self.second * other
             )
        return NotImplemented
    
    def __rmul__(self, other):
         return self.__mul__(other)
    
    
    def __add__(self, other : "Pair") -> "Pair":
         return Pair(
            self.first + other.first,
            self.second + other.second,
        )
    
    def __sub__(self, other : "Pair") -> "Pair":
         return Pair(
            self.first - other.first,
            self.second - other.second,
        )
         
    def length(self) -> float:
         return math.hypot(self.first, self.second)



def normalize_vector(vector : Pair) -> Pair:
        length = math.sqrt(vector.first ** 2 + vector.second ** 2)
        if length == 0:
             return Pair(0, 0)
        new_vector = Pair(vector.first / length, vector.second / length)
        return new_vector



@dataclass
class Puck:
    position : Pair
    speed : float
    speed_vector : Pair

    RADIUS : int = PUCK_RADIUS

    def __init__(self, position : Pair, speed : int, speed_vector : Pair):
        self.position = position
        self.speed = speed
        self.speed_vector = normalize_vector(speed_vector)

    




@dataclass
class Player:
     position : Pair
     speed : float
     speed_vector : Pair

     RADIUS = PLAYER_RADIUS

     def __init__(self, position : Pair, speed : float, speed_vector : Pair):
          self.position = position
          self.speed = speed
          self.speed_vector = normalize_vector(speed_vector)



@dataclass 
class GameState:
     player1 : Player
     player2 : Player
     puck : Puck
     score : Pair


class Status(IntEnum):
     NO_PLAYERS = 0
     WAITING_FOR_OTHER_PLAYER = 1
     READY = 2



class WebSocketHandler:
     player1 : WebSocket | None
     player2 : WebSocket | None
     status : Status

     def __init__(self):
          self.player1 = None
          self.player2 = None
          self.status = Status.NO_PLAYERS
          self.lock = asyncio.Lock()


     def number_of_connected_players(self) -> int:
          connected_players = 0
          if isinstance(self.player1, WebSocket):
               connected_players += 1
          if isinstance(self.player2, WebSocket):
               connected_players += 1
          return connected_players


     async def connect(self, websocket : WebSocket) -> bool:
          await websocket.accept()

          async with self.lock:
               if self.player1 is None:
                    self.player1 = websocket
               elif self.player2 is None:
                    self.player2 = websocket
               else:
                    await websocket.close()
                    return False
               self.status = Status(self.number_of_connected_players())
               return True


     async def disconnect(self, websocket : WebSocket):

          async with self.lock:
               if websocket is self.player1:
                    self.player1 = None
               elif websocket is self.player2:
                    self.player2 = None
               self.status = Status(self.number_of_connected_players())
               return



     #message data type - dict
     #need to serialize GameState to dict with asdict(game_state)
     async def send_to_player1(self, message : dict):
          if isinstance(self.player1, WebSocket):
               await self.player1.send_json(message)
          else:
               raise RuntimeError("Player 1 is not connected. Trying to send a message with no connection")          

     async def send_to_player2(self, message : dict):
          if isinstance(self.player2, WebSocket):
               #reverse data across the (0,0) coordinate here
               await self.player2.send_json(message)
          else:
               raise RuntimeError("Player 2 is not connected. Trying to send a message with no connection")     
          
     
     
class GameMaster():
     gamestate : GameState

     def __init__(self):
          self.gamestate.player1 = None
          self.gamestate.player2 = None
          self.gamestate.puck = None
          self.gamestate.score = None

     def StartGame(self, player1 : Player, player2 : Player):
          self.gamestate.player1 = player1
          self.gamestate.player1.position = Pair(0, DOWN_WALL + PLAYER_RADIUS)

          self.gamestate.player2 = player2
          self.gamestate.player2.position = Pair(0, TOP_WALL - PLAYER_RADIUS)

          puck = Puck(Pair(0,0), 0, Pair(0,0))
          self.gamestate.puck = puck

          self.gamestate.score = Pair(0,0)

     
     def EndGameDisconnect(self):
          self.gamestate.puck.speed = 0
          app.state.web_handler.send_to_player1({})


     def EndGameScore(self):
          self.gamestate.puck.speed = 0


class Master():
     gameMaster : GameMaster
     wsHandler : WebSocketHandler
     #inputHandler


     def __init__(self):
          pass

class InputHandler:

     def __init__(self):
          self._history = {
               1 : deque(maxlen = 2),
               2 : deque(maxlen = 2)
          }
          self._lock = asyncio.Lock()



#packet_data MUST look like 
#{
# "position": {
#     "x": 153.2,
#     "y": 421.6
# }
#}

     async def store_packet(self, player_id : int, packet_data : dict):
          async with self._lock:
               self._history[player_id].append(
                    Pair(first = packet_data["position"]["x"],
                         second = packet_data["position"]["y"])
               )



     async def get_last_packets(self, player_id : int):
          async with self._lock:
               if len(self._history[player_id]) < 2:
                    return None
               
               return tuple(self._history[player_id])


