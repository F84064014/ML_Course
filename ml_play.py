"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import numpy as np
import pickle
from os import path

def pdty(x, y, vx, vy):
    time = abs((y-260)/abs(vy+0.1))
    if vx < 0:
        hit_y = y-(x/abs(vx))*abs(vy)
        if 0 <= x+vx*time and x+vx*time <=200:
            return x+vx*time
        else:
            return pdty(0, hit_y, -vx, vy)
    if vx > 0:
        hit_y = y-((200-x)/vx)*abs(vy)
        if 0 <= x+vx*time and x+vx*time <= 200:
            return x+vx*time
        else:
            return pdty(200,hit_y,-vx,vy)
    else:
        return 80


def pdtx(x, y, vx, vy):
    time = abs((420-y)/abs(vy+0.1))
    if vx < 0:
        hity = y+(x/abs(vx))*abs(vy)
        if 0 <= x+vx*time and x+vx*time <= 200:
            return x+vx*time
        else:
            return pdtx(0, hity, -vx, vy)
    if vx > 0:
        hity = y+((200-x)/vx)*abs(vy)
        if 0 <= x+vx*time and x+vx*time <= 200:
            return x+vx*time
        else:
            return pdtx(200, hity, -vx, vy)
    else:
        return 80

def get_dir(vx, vy):
    if vx>0 and vy >0:
        return 0
    elif vx>0 and vy<0:
        return 1
    elif vx<0 and vy>0:
        return 0
    elif vx<0 and vy<0:
        return 2
    else:
        return 0

def ml_loop(side: str):
    """
    The main loop for the machine learning process

    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```

    @param side The side which this script is executed for. Either "1P" or "2P".
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    sx = 0
    sy = 0
    sb = 0
    est = 0

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information
        x = scene_info["ball"][0]
        y = scene_info["ball"][1]
        platx1 = scene_info["platform_1P"][0]
        platy1 = scene_info["platform_1P"][1]
        blockx = scene_info["blocker"][0]
        vb = blockx-sb
        vx = x-sx
        vy = y-sy
        sx = x
        sy = y
        dir_ball1 = get_dir(vx, vy)
        #if vx < 7:
        #    vx = -7
        #if vy < 7:
        #    vy = 7

        #Feature1
        feat1 = []
        feat1.append((x-100))
        feat1.append(y)
        feat1.append(platx1)
        feat1.append(vx)
        feat1.append(vy)
        feat1.append(dir_ball1)
        feat1.append(pdtx(x,y,vx,vy))
        feat1 = np.array(feat1)
        feat1 = feat1.reshape((-1, len(feat1)))

        #filename = path.join(path.dirname(__file__), 'P1ml.pickle')
        #p1ml = pickle.load(open(filename, 'rb'))

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            ball_served = True      
        elif y < 421 and y > 420-vy and vy >0:
            if blockx > 100:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
            elif blockx < 70:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})     
            else:
                if vb > 0:
                    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                else:
                    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
        else:
            est = pdtx(x,y,vx,vy)
            if platx1 < (est-15):
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})            
            #y = p1ml.predict(feat1)
            #if y <= 0.5:
            #    comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            #elif y > 0.5 and y <= 1.5:
            #    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
            #elif y > 1.5:
            #    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
