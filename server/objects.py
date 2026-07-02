from dataclasses import dataclass
from typing import overload
from fastapi import WebSocket, WebSocketDisconnect
from enum import IntEnum
from constants import *
from collections import deque
import math
import asyncio
from source import app
from physics_engine import calculate_player_puck_collision, calculate_player_wall_collision, calculate_puck_wall_collision, checking_goal

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
     masterLink : "Master"

     def __init__(self, master : "Master"):
          self.player1 = None
          self.player2 = None
          self.status = Status.NO_PLAYERS
          self.lock = asyncio.Lock()
          self.masterLink = master


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
               if self.status == Status.READY:
                    self.masterLink.gameMaster.StartGame(player1 = Player(Pair(0,0), 0, Pair(0,0)), 
                                                         player2 = Player(Pair(0,0), 0, Pair(0,0)))
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
     
     async def send_to_both_players(self, message : dict):
          successfully_sent = True
          if isinstance(self.player1, WebSocket):
               await self.player1.send_json(message)
          else:
               successfully_sent = False
          
          if isinstance(self.player2, WebSocket):
               await self.player2.send_json(message)
          else:
               successfully_sent = False
          
          return successfully_sent

          
          

          

     
class GameMaster():
     gamestate : GameState
     masterLink : "Master"
     time_delta : float = 1/60

     def __init__(self, master : "Master"):
          GameState(
               player1 = Player(Pair(0,0), 0, Pair(0,0)),
               player2 = Player(Pair(0,0), 0, Pair(0,0)),
               puck = Puck(Pair(0,0), 0, Pair(0,0)),
               score = Pair(0,0)
          )
          self.masterLink = master

     def StartGame(self, player1 : Player, player2 : Player):
          self.gamestate.player1 = player1
          self.gamestate.player1.position = Pair(0, DOWN_WALL + PLAYER_RADIUS)

          self.gamestate.player2 = player2
          self.gamestate.player2.position = Pair(0, TOP_WALL - PLAYER_RADIUS)

          puck = Puck(Pair(0,0), 0, Pair(0,0))
          self.gamestate.puck = puck

          self.gamestate.score = Pair(0,0)


          asyncio.create_task(self.gameLoop())

     
     async def EndGameDisconnect(self):
          self.gamestate.puck.speed = 0
          await self.masterLink.wsHandler.send_to_both_players(
               {"message" : "one of the players disconnected. the game stops now"}
          )
          #отправляем сам месседж


     async def EndGameScore(self):
          self.gamestate.puck.speed = 0
          await self.masterLink.wsHandler.send_to_both_players(
               {"message" : "score reached"}
          )#отправляем месседж




     def update_data_for_player1(self):
          last_two_packets_for_player1 = self.masterLink.inputHandler.get_last_packets(1)

          #если еще нет двух пакетов ничего не происходит
          if last_two_packets_for_player1 is None:
               return 

          self.gamestate.player1.position = Pair(last_two_packets_for_player1[1].first, last_two_packets_for_player1[1].second)
                  #обновляем позицию player1
          self.gamestate.player1.speed_vector = Pair(last_two_packets_for_player1[1].first - last_two_packets_for_player1[0].first,
                                        last_two_packets_for_player1[1].second - last_two_packets_for_player1[0].second)       #считаем вектор скорости по последним двум пакетам данных (за 1/60 секунды!!)
          self.gamestate.player1.speed = self.gamestate.player1.speed_vector.length() 
          self.gamestate.player1.speed_vector = normalize_vector(self.gamestate.player1.speed_vector)


          self.gamestate.player1.speed_vector = calculate_player_wall_collision(self.gamestate.player1, 1)                      #чекаем коллизию player1 и стен
          self.gamestate.player1.speed = self.gamestate.player1.speed_vector.length()
          self.gamestate.player1.speed_vector = normalize_vector(self.gamestate.player1.speed_vector)

          if self.gamestate.player1.speed > SPEED_LIMIT:
               self.gamestate.player1.speed = SPEED_LIMIT



     def update_data_for_player2(self):
          last_two_packets_for_player2 = self.masterLink.inputHandler.get_last_packets(2)

          #если нет двух пакетов
          if last_two_packets_for_player2 is None:
               return

          self.gamestate.player2.position = Pair(last_two_packets_for_player2[1].first, last_two_packets_for_player2[1].second)
                  #обновляем позицию player1
          self.gamestate.player2.speed_vector = Pair(last_two_packets_for_player2[1].first - last_two_packets_for_player2[0].first,
                                                     last_two_packets_for_player2[1].second - last_two_packets_for_player2[0].second)       #считаем вектор скорости по последним двум пакетам данных
          self.gamestate.player2.speed = self.gamestate.player2.speed_vector.length() 
          self.gamestate.player2.speed_vector = normalize_vector(self.gamestate.player2.speed_vector)

          self.gamestate.player2.speed_vector = calculate_player_wall_collision(self.gamestate.player2, 2)                      #чекаем коллизию player2 и стен
          self.gamestate.player2.speed = self.gamestate.player2.speed_vector.length() 
          self.gamestate.player2.speed_vector = normalize_vector(self.gamestate.player2.speed_vector)

          if self.gamestate.player2.speed > SPEED_LIMIT:
               self.gamestate.player2.speed = SPEED_LIMIT



     def update_puck_data(self):
          
          if (self.gamestate.puck.speed - PUCK_FRICTION) > 0:
               self.gamestate.puck.speed = self.gamestate.puck.speed - PUCK_FRICTION
          else:
               self.gamestate.puck.speed = 0


          self.gamestate.puck.position = self.gamestate.puck.position + self.gamestate.puck.speed_vector * self.gamestate.puck.speed  #обновляем позицию шайбы
          

          self.gamestate.puck.speed_vector = calculate_puck_wall_collision(self.gamestate.puck)                                                                      #чекаем коллизию шайбы и стены и обновляем вектор скорости
          self.gamestate.puck.speed = self.gamestate.puck.speed_vector.length() 
          self.gamestate.puck.speed_vector = normalize_vector(self.gamestate.puck.speed_vector)

          self.gamestate.puck.speed_vector = calculate_player_puck_collision(self.gamestate.player1, self.gamestate.puck)                                  #чекаем коллизию шайбы и player1 и обновляем вектор скорости
          self.gamestate.puck.speed = self.gamestate.puck.speed_vector.length() 
          self.gamestate.puck.speed_vector = normalize_vector(self.gamestate.puck.speed_vector)

          self.gamestate.puck.speed_vector = calculate_player_puck_collision(self.gamestate.player2, self.gamestate.puck)                        #чекаем коллизию шайбы и player2 и обновляем вектор скорости
          self.gamestate.puck.speed = self.gamestate.puck.speed_vector.length() 
          self.gamestate.puck.speed_vector = normalize_vector(self.gamestate.puck.speed_vector)

          if self.gamestate.puck.speed > SPEED_LIMIT:
               self.gamestate.puck.speed = SPEED_LIMIT


     async def gameLoop(self):

          while True:
               self.update_data_for_player1()     #player1 обновляем
               self.update_data_for_player2()     #player2 обновляем
               self.update_puck_data()        #puck обновляем

               goal_status : GoalStatus = checking_goal(self.gamestate.puck)

               if goal_status == GoalStatus.Player1Scored:
                    self.gamestate.score.first =  self.gamestate.score.first + 1
                    #self.masterLink.wsHandler.send_to_both_players() #send to both players msg about goal
               elif goal_status == GoalStatus.Player2Scored:
                    self.gamestate.score.second =  self.gamestate.score.second + 1
                    #self.masterLink.wsHandler.send_to_both_players() #send to both players msg about goal

                    #в идеале, можно разделить сообщения на типы, чтобы клиенту было легче их обрабатывать
                    #например - message, error, GameState, GoalStatus

               await asyncio.sleep(self.time_delta)



               
               

class Master():
     gameMaster : GameMaster
     wsHandler : WebSocketHandler
     inputHandler : "InputHandler"


     def __init__(self):
          self.gameMaster = GameMaster(self)
          self.wsHandler = WebSocketHandler(self)
          self.inputHandler = InputHandler()




class InputHandler:

     def __init__(self):
          self._history = {
               1 : deque(maxlen = 2),
               2 : deque(maxlen = 2)
          }
          



#packet_data MUST look like 
#{
# "position": {
#     "x": 153.2,
#     "y": 421.6
# }
#}

     def store_packet(self, player_id : int, packet_data : dict):
          self._history[player_id].append(
               Pair(first = packet_data["position"]["x"],
                    second = packet_data["position"]["y"])
               )



     def get_last_packets(self, player_id : int):
          if len(self._history[player_id]) < 2:
               return None
               
          return tuple(self._history[player_id])


class GoalStatus(IntEnum):
     NoGoal = 0
     Player1Scored = 1
     Player2Scored = 2