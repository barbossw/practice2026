import os
import sys
import math
import pytest

# Добавляем папку 'server' в пути поиска Python, 
# чтобы серверные файлы могли без проблем импортировать друг друга.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'server')))

# Теперь импортируем модули так же, как это делает сам сервер (без server.)
from models import Pair, Player, Puck, GoalStatus, normalize_vector
from physics_engine import (
    checking_goal,
    calculate_puck_wall_collision,
    calculate_player_wall_collision
)
from constants import LEFT_WALL, RIGHT_WALL, TOP_WALL, DOWN_WALL, PUCK_RADIUS


def test_pair_operations():
    p1 = Pair(3.0, 4.0)
    p2 = Pair(1.0, 2.0)
    
    assert (p1 + p2) == Pair(4.0, 6.0)
    assert (p1 - p2) == Pair(2.0, 2.0)
    assert p1.length() == 5.0
    assert (p1 * 2) == Pair(6.0, 8.0)
    assert (p1 * p2) == 11.0

def test_normalize_vector():
    zero_vec = Pair(0.0, 0.0)
    assert normalize_vector(zero_vec) == Pair(0.0, 0.0)
    
    vec = Pair(3.0, 4.0)
    norm = normalize_vector(vec)
    assert math.isclose(norm.first, 0.6)
    assert math.isclose(norm.second, 0.8)

def test_checking_goal_no_goal():
    puck = Puck(position=Pair(0.0, 0.0), speed=5.0, speed_vector=Pair(1.0, 0.0))
    assert checking_goal(puck) == GoalStatus.NoGoal

def test_checking_goal_player1_scored():
    puck_pos = Pair(0.0, TOP_WALL + PUCK_RADIUS + 10.0)
    puck = Puck(position=puck_pos, speed=10.0, speed_vector=Pair(0.0, 1.0))
    assert checking_goal(puck) == GoalStatus.Player1Scored

def test_calculate_puck_wall_collision_left_wall():
    puck = Puck(position=Pair(LEFT_WALL + PUCK_RADIUS - 1.0, 0.0), 
                speed=10.0, 
                speed_vector=Pair(-1.0, 0.0))
    new_speed_vector = calculate_puck_wall_collision(puck)
    
    assert new_speed_vector.first > 0.0
    assert new_speed_vector.second == 0.0
    assert puck.position.first == LEFT_WALL + PUCK_RADIUS

def test_calculate_player_wall_collision():
    player = Player(position=Pair(RIGHT_WALL + 10.0, 0.0), 
                    speed=5.0, 
                    speed_vector=Pair(1.0, 0.0))
    speed_vector = calculate_player_wall_collision(player, player_id=1)
    assert speed_vector.first == 0.0