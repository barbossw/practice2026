PUCK_RADIUS = 20

PLAYER_RADIUS = 50

LEFT_WALL = -200.0
RIGHT_WALL = 200.0

TOP_WALL = 300.0
DOWN_WALL = -300.0

GOAL_LEFT = -100.0
GOAL_RIGHT = 100.0

SPEED_LIMIT = 50.0

PUCK_FRICTION = 0.5
#за 1/60 секунды



"""
note:formarts the server sends / receives:

receive inside /ws_connect endpoint:
{
    "position": {
        "x": 153.2,
        "y": 421.6
    }
}

sends to players:

send_json(asdict(GameState))

which will look like:

{
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
            "first": 700,
            "second": 250
        },
        "speed": 5,
        "speed_vector": {
            "first": -1.0,
            "second": 0.0
        }
    },
    "puck": {
        "position": {
            "first": 400,
            "second": 250
        },
        "speed": 8,
        "speed_vector": {
            "first": 0.7071067811865475,
            "second": 0.7071067811865475
        }
    },
    "score": {
        "first": 2,
        "second": 3
    }
}


"""