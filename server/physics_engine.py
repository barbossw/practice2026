from objects import Pair, Player, Puck
from constants import*



def calculate_player_puck_collision(player : Player, puck : Puck) -> tuple[float, Pair]:
    player_speed = player.speed_vector * player.speed
    puck_speed = puck.speed_vector * puck.speed

    #formula : v'' = v' - 2(v' * n)n , где n единичная нормаль к прямой
    #по относительности v' = v(puck) - v(player)

    puck_speed_relative = puck_speed - player_speed
    normal_vector = puck.position - player.position
    normal_vector_unit = normal_vector * (1/normal_vector.length())

    puck_speed_relative_reflected = (puck_speed_relative - normal_vector_unit * ( 2*(puck_speed_relative * normal_vector_unit) ) )
    puck_speed_reflected = puck_speed_relative_reflected + player_speed

    return puck_speed_reflected.length(), (puck_speed_reflected * (1/puck_speed_reflected.length()))




def calculate_puck_wall_collision(puck : Puck):
    puck_speed_vector = puck.speed_vector * puck.speed
    if ((puck.position.first <= (LEFT_WALL + PUCK_RADIUS)) or           #проверка на коллизию с левой стенкой
        ((puck.position.second <= (TOP_WALL - PUCK_RADIUS) or           #проверка нахождения шайбы в воротах + коллизия с их левой стенкой
          puck.position.second >= (DOWN_WALL + PUCK_RADIUS)) and 
         puck.position.first <= (GOAL_LEFT + PUCK_RADIUS))
         or
         ((puck.position.first >= (RIGHT_WALL - PUCK_RADIUS)) or      #проверка на коллизию с правой стенкой
          ((puck.position.second <= (TOP_WALL - PUCK_RADIUS) or         #проверка на нахождение шайбы в воротах + коллизия с их правой стенкой
          puck.position.second >= (DOWN_WALL + PUCK_RADIUS)) and 
         puck.position.first >= (GOAL_RIGHT - PUCK_RADIUS)))):
        normal_vector_from_wall = Pair(1, 0)
        new_puck_speed_vector = puck_speed_vector - normal_vector_from_wall * (puck_speed_vector * normal_vector_from_wall) * 2

    elif ((puck.position.second >= (TOP_WALL - PUCK_RADIUS) or          #проверка на коллизию с горизонтальными стенками возле ворот
           puck.position.second <= (DOWN_WALL + PUCK_RADIUS)) and 

          (puck.position.first <= (GOAL_LEFT + PUCK_RADIUS) or 
           puck.position.first >= (GOAL_RIGHT - PUCK_RADIUS))):
        normal_vector_from_wall = Pair(0, 1)
        new_puck_speed_vector = puck_speed_vector - normal_vector_from_wall * (puck_speed_vector * normal_vector_from_wall) * 2
    
    return new_puck_speed_vector

