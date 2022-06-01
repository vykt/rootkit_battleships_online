# game.py

import sys
import socket

import map
import draw


'''
Functionality of the game.py file has been substantially expanded upon
with networking functions residing in this file. With the player.py file
dissipating, half of its functionality went to game.py

'''


#Check for victory conditions for a single player
#return: 0 - fail, 1 - victory
def check_win(map_arr, dim_x, dim_y):
    
    '''
    Another solution is to keep track of a number of remaining ship tiles
    and decrement them by 1 each time a ship hit is scored. This however
    adds even more arguments to already cumbersome functions. Therefore
    this approach is used, even if it has slighly more overhead.

    '''
    for i in range(dim_x):
        for j in range(dim_y):
            if map_arr[i][j] == 'S':
                return 0

    return 1


#connection failed
def exit_conn():
    sys.exit("Connection terminated, exiting...")

#requested or expected exit
def exit_normal():
    sys.exit("Exiting Battleships Online...")

#something went wrong
def exit_unexpected():
    sys.exit("Unexpected behaviour, exiting...")


#send data with error check
def safe_send(sock, buf):
    try:
        sock.send(bytes(buf, "utf-8"))
    except:
        sock.close()
        exit_conn()


#receive data with error check
def safe_recv(sock):
    try:
        buf = sock.recv(128).decode("utf-8")
    except:
        exit_conn()
    if buf == '':
        sock.close()
        exit_conn()
    else:
        return buf


#Handle the opponent sending attack
def handle_attack(map_arr, size_x, size_y, sock):
    print("Waiting for opponent to attack...")
    ret, tgt_x, tgt_y = map.map_manage_attack(map_arr, size_x, size_y, sock)
    if ret == -1:
        print("Enemy missed on ", chr(ord('A')+tgt_y), tgt_x)
    elif ret == -2:
        print("Enemy hit on ", chr(ord('A')+tgt_y), tgt_x)
    elif ret == -3:
        draw.print_map(map_arr, size_x, size_y, True)
        draw.print_map(enemy_map_arr, size_x, size_y, False)
        print("\nAll of your ships are destroyed! You lose!")
        exit_normal()
