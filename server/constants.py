PUCK_RADIUS = 20
PLAYER_RADIUS = 50


LEFT_WALL = -200.0
RIGHT_WALL = 200.0

TOP_WALL = 300.0
DOWN_WALL = -300.0

GOAL_LEFT = -100.0
GOAL_RIGHT = 100.0

PLAYER_SPEED_LIMIT = 9
PUCK_SPEED_LIMIT = 6

PUCK_FRICTION = 0.005
#за 1/120 секунды

GAMEMODE_HANDSHAKE_TIMEOUT = 5

DEFAULT_CONFIG : dict = {
    "PUCK_RADIUS" : 20,
    "PLAYER_RADIUS" : 50,
    "MAX_SCORE" : 5
}


#copies of the default - change later according to gamemodes
CONFIG_GAMEMODE_2 : dict = {
    "PUCK_RADIUS" : 20,
    "PLAYER_RADIUS" : 50,
    "MAX_SCORE" : 5
}

CONFIG_GAMEMODE_3 : dict = {
    "PUCK_RADIUS" : 20,
    "PLAYER_RADIUS" : 50,
    "MAX_SCORE" : 5
}


"""
note:formarts the server sends / receives:

receive inside /ws_connect endpoint:

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
sends to players:

{
    "type": "GameState",
    "data": {
        "player1": {
            "position": {
                "first": 100,
                "second": 250
            },
            "speed": 5,
            "speed_vector": {
                "first": 1.0,
                "second": 0.0
            }
        },
        "player2": {
             "position": {
                "first": -100,
                "second": -50
            },
            "speed": 5,
            "speed_vector": {
                "first": 0.0,
                "second": 1.0
            }
        },
        "puck": {
            "position": {
                "first": 100,
                "second": 250
            },
            "speed": 5,
            "speed_vector": {
                "first": 1.0,
                "second": 0.0
            }
        },
        "score": {
            "first": 2,
            "second": 3
        }
    }
}

"""