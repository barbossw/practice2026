from objects import Pair, Player, Puck



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