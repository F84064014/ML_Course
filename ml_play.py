"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm

def P2_loop():
    comm.ml_ready()
    prev_x = 0
    prev_y = 0
    prev_bx = 0
    while True:
        scene_info = comm.recv_from_game()
        if scene_info["status"] != "GAME_ALIVE":
            prev_x = scene_info["ball"][0]
            prev_y = scene_info["ball"][1]
            comm.ml_ready()
            continue
        dx = scene_info["ball"][0] - prev_x
        dy = scene_info["ball"][1] - prev_y
        prev_x = scene_info["ball"][0]
        prev_y = scene_info["ball"][1]
        bdx = scene_info["blocker"][0] - prev_bx
        prev_bx = scene_info["blocker"][0]
        
        if dy == 0:
            continue
        
        rtn_val = -100
        if dy > 0:
            if prev_y < 235: # go down
                rtn_val = p2_bounce(prev_x, prev_y, dx, dy, prev_bx, bdx, 0)
            else:
                rtn_val = p2_downward(prev_x, prev_y, dx, dy, prev_bx, bdx)
        else:   # go up
            if prev_y + dy <= 80:
                if p2_bounce(prev_x + dx, 80, dx, -dy, prev_bx, bdx, 1) == True:
                    if dx > 0:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                    else:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                else:
                    if dx < 0:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                    else:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                continue
            if prev_y < 235:
                rtn_val = p2_bounce_back(prev_x, prev_y, dx, dy)
            else:
                rtn_val = p2_upward(prev_x, prev_y, dx, dy, prev_bx, bdx)
        
        if scene_info["platform_2P"][0] + 20 > rtn_val + 14:
            comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
        elif scene_info["platform_2P"][0] + 20 < rtn_val - 14:
            comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})

def p2_bounce(x, y, dx, dy, bx, bdx, flag):
    while y < 235:
        bx += bdx
        if bx >= 170:
            bx = 170
            bdx = - bdx
        elif bx <= 0:
            bx = 0
            bdx = -bdx

        y += dy
        x += dx
        if x >= 195:
            x = 195
            dx = -dx
        elif x <= 0:
            x = 0
            dx = -dx

    if x >= bx - 5 and x <= bx + 30:
        if flag == 1:
            return True
        return p2_bounce_back(x, y, dx, -dy)
    else:
        if flag == 1:
            return False
        return p2_downward(x, y, dx, dy, bx, bdx)
    
def p2_bounce_back(x, y, dx, dy):
    while y > 80:
        y += dy
        x += dx
        if x >= 195:
            x = 195
            dx = -dx
        elif x <= 0:
            x = 0
            dx = -dx
    return x

def p2_downward(x, y, dx, dy, bx, bdx):
    while y < 415:
        bx += bdx
        if bx >= 170:
            bx = 170
            bdx = - bdx
        elif bx <= 0:
            bx = 0
            bdx = -bdx
        
        y += dy
        x += dx
        if y <= 260 and x >= bx - 5 and x <= bx + 30:
            dx = -dx
        elif x >= 195:
            x = 195
            dx = -dx
        elif x <= 0:
            x = 0
            dx = -dx
    y = 415
    dy = -dy
    return p2_upward(x, y, dx, dy, bx, bdx)

def p2_upward(x, y, dx, dy, bx, bdx):
    while y > 235:
        bx += bdx
        if bx >= 170:
            bx = 170
            bdx = - bdx
        elif bx <= 0:
            bx = 0
            bdx = -bdx
        
        y += dy
        x += dx
        if y <= 260 and x >= bx - 5 and x <= bx + 30:
            dx = -dx
        elif x >= 195:
            x = 195
            dx = -dx
        elif x <= 0:
            x = 0
            dx = -dx
    return p2_bounce_back(x, y, dx, dy)

def P1_loop():
    comm.ml_ready()
    prev_x = 0
    prev_y = 0
    prev_bx = 0
    while True:
        scene_info = comm.recv_from_game()
        if scene_info["status"] != "GAME_ALIVE":
            prev_x = scene_info["ball"][0]
            prev_y = scene_info["ball"][1]
            comm.ml_ready()
            continue
        dx = scene_info["ball"][0] - prev_x
        dy = scene_info["ball"][1] - prev_y
        prev_x = scene_info["ball"][0]
        prev_y = scene_info["ball"][1]
        bdx = scene_info["blocker"][0] - prev_bx
        prev_bx = scene_info["blocker"][0]
        if dy == 0:
            continue
        
        rtn_val = -100
        if dy < 0: # go up
            if prev_y > 260:
                rtn_val = p1_bounce(prev_x, prev_y, dx, dy, prev_bx, bdx, 0)
            else:
                rtn_val = p1_upward(prev_x, prev_y, dx, dy, prev_bx, bdx)
        else:   # go down
            if prev_y + dy >= 415:
                if p1_bounce(prev_x + dx, 415, dx, -dy, prev_bx, bdx, 1) == True:
                    if dx > 0:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                    else:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                else:
                    if dx < 0:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                    else:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                continue
            if prev_y > 260:
                rtn_val = p1_bounce_back(prev_x, prev_y, dx, dy)
            else:
                rtn_val = p1_downward(prev_x, prev_y, dx, dy, prev_bx, bdx)
        
        if scene_info["platform_1P"][0] + 20 > rtn_val + 14:
            comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
        elif scene_info["platform_1P"][0] + 20 < rtn_val - 14:
            comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})

def p1_bounce(x, y, dx, dy, bx, bdx, flag):
    while y > 260:
        bx += bdx
        if bx >= 170:
            bx = 170
            bdx = - bdx
        elif bx <= 0:
            bx = 0
            bdx = -bdx

        y += dy
        x += dx
        if x >= 195:
            x = 195
            dx = -dx
        elif x <= 0:
            x = 0
            dx = -dx

    if x >= bx - 5 and x <= bx + 30:
        if flag == 1:
            return True
        return p1_bounce_back(x, y, dx, -dy)
    else:
        if flag == 1:
            return False
        return p1_upward(x, y, dx, dy, bx, bdx)
    
def p1_bounce_back(x, y, dx, dy):
    while y < 415:
        y += dy
        x += dx
        if x >= 195:
            x = 195
            dx = -dx
        elif x <= 0:
            x = 0
            dx = -dx
    return x

def p1_upward(x, y, dx, dy, bx, bdx):
    while y > 80:
        bx += bdx
        if bx >= 170:
            bx = 170
            bdx = - bdx
        elif bx <= 0:
            bx = 0
            bdx = -bdx
        
        y += dy
        x += dx
        if y >= 235 and x >= bx - 5 and x <= bx + 30:
            dx = -dx
        elif x >= 195:
            x = 195
            dx = -dx
        elif x <= 0:
            x = 0
            dx = -dx
    y = 80
    dy = -dy
    return (p1_downward(x, y, dx, dy, bx, bdx) + p1_downward(x, y, -dx, dy, bx, bdx)) / 2

def p1_downward(x, y, dx, dy, bx, bdx):
    while y < 260:
        bx += bdx
        if bx >= 170:
            bx = 170
            bdx = - bdx
        elif bx <= 0:
            bx = 0
            bdx = -bdx
        
        y += dy
        x += dx
        if y >= 235 and x >= bx - 5 and x <= bx + 30:
            dx = -dx
        elif x >= 195:
            x = 195
            dx = -dx
        elif x <= 0:
            x = 0
            dx = -dx
    return p1_bounce_back(x, y, dx, dy)

def ml_loop(side: str):
    if side == '2P':
        P2_loop()
    else:
        P1_loop()
