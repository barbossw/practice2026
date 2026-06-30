from dataclasses import dataclass
import constants
import math

@dataclass
class Pair:
    first : float
    second : float

def normalize_vector(vector : Pair) -> Pair:
        length = math.sqrt(vector.first ** 2 + vector.second ** 2)
        new_vector = Pair(vector.first / length, vector.second / length)
        return new_vector


@dataclass
class Puck:
    position : Pair
    speed : float
    speed_vector : Pair

    MASS : int = constants.PUCK_MASS
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

     MASS = constants.PLAYER_MASS
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
