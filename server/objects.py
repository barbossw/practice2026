from dataclasses import dataclass
from typing import overload
import constants
import math

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
        new_vector = Pair(vector.first / length, vector.second / length)
        return new_vector



@dataclass
class Puck:
    position : Pair
    speed : float
    speed_vector : Pair

    RADIUS : int = constants.PUCK_RADIUS

    def __init__(self, position : Pair, speed : int, speed_vector : Pair):
        self.position = position
        self.speed = speed
        self.speed_vector = normalize_vector(speed_vector)

    




@dataclass
class Player:
     position : Pair
     speed : float
     speed_vector : Pair

     RADIUS = constants.PLAYER_RADIUS

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
