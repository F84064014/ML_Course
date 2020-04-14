"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False

    lowest = -1 #lowest block position
    lock = False #locker
    old_x = 0
    old_y = 0
    est = -1 # the estimate position of x

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        ball_x = scene_info.ball[0]
        ball_y = scene_info.ball[1]
        plat_x = scene_info.platform[0]
        plat_y = scene_info.platform[1]

        for x in scene_info.bricks:
            if x[1] > lowest:
                lowest = x[1]
        for x in scene_info.hard_bricks:
            if x[1] > lowest:
                lowest = x[1]
        #print(scene_info.ball)
        #print("con1" + str(ball_y>(lowest+10)))
        #print("con2" + str(not lock))
        #print("con3" + str(ball_y-old_y))
        #print(est)

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            if scene_info.platform[0] < 30:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            elif scene_info.platform[0] > 30:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_RIGHT)
                ball_served = True
        elif lock == True:
            if ball_y == plat_y-5:
                print("unlock")
                lock = False
            if plat_y-ball_y <= 15:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            #elif ball_y > 370:
            #    if ball_x < plat_x:
            #        comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            #    elif ball_x > plat_x:
            #        comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            #    else:
            #        comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            elif plat_x > est-15:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            elif plat_x < est-15:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)    
        elif ball_y > (lowest+10) and not lock and (ball_y - old_y) > 0:
            lock = True
            print("locked")
            vy = (ball_y-old_y)
            vx = abs(ball_x-old_x) #velocity of x
            if vx < 7:
                vx = 7
            #print("velocity of x =" + str(vx))
            #print("velocity of y =" + str(vy))
            #plat_y = 400
            if ball_x - old_x > 0: #move right
                print('MR')
                if (200-ball_x)/vx > (plat_y-ball_y)/vy:
                    est = (plat_y-ball_y)/vy*vx+ball_x
                else: #hit x = 200
                    hit_y = ball_y+(200-ball_x)/vx*vy
                    est = 200 - (plat_y-hit_y)/vy*vx
            else: #move left
                print("ML")
                if (ball_x-0)/vx > (plat_y-ball_y)/vy:
                    est = ball_x-(plat_y-ball_y)/vy*vx
                else: #hit x = 0
                    hit_y = ball_y+ball_x/vx*vy
                    est = (plat_y-hit_y)/(ball_y-old_y)*vx
            print("begin with " + str(ball_x) + "," + str(ball_y))
            print("est=" + str(est))
            comm.send_instruction(scene_info.frame, PlatformAction.NONE)
        else:
            if plat_x < 85:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            elif plat_x > 85:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
        
        old_x = ball_x
        old_y = ball_y
