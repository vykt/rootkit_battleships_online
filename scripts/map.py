# map.py
import socket
import random
import copy
from datetime import datetime

import draw
import game


'''
Handles mapping like before. For online gameplay, behaviour of predominantly
map_place_attack changed. map_manage_attack also added to handle responses to
map_place_attack.

'''



'''
        MAP VALUES

- = empty
S = ship present    T = temporary ship present
X = ship hit
m = missed shot

'''


#check the tile is valid by checking surroundings
#return: 1 - success, 0 - fail | TODO swap around
def map_place_ship_tile_validate(map_arr_copy, xpos, ypos, dim_x, dim_y):
    
    check_pass = 1
    temp_x = -1
    temp_y = -1
    x_diff = [0, 1, 0, -1, 0]
    y_diff = [0, 0, 1, 0, -1]


    #check bounds for xpos & ypos
    if xpos >= dim_x or xpos < 0 or ypos >= dim_y or ypos < 0:
        check_pass = 0
        return check_pass

    #check surrounding tiles
    for i in range(0, 5):
        temp_x = xpos + x_diff[i]
        temp_y = ypos + y_diff[i]
        #if the modified value now falls outside the bounds of the map
        if temp_x >= dim_x or temp_x < 0 or \
           temp_y >= dim_y or temp_y < 0:
            continue
        #else it is still within the bounds
        else:
            if map_arr_copy[temp_x][temp_y] == '-' or \
               map_arr_copy[temp_x][temp_y] == 'T':
                continue
            else:
                check_pass = 0
                break
    
    return check_pass


#place ships on the map
#return: 0 - success, 1 - fail
def map_place_ship(map_arr, ship_template, ship, direction, xpos, ypos, dim_x, dim_y):

    map_arr_copy = copy.deepcopy(map_arr)
    check_ret = -1
    temp_x = -1
    temp_y = -1

    #decide which way the ship's going
    for i in range(ship_template[ship]):
        if direction == -1:
            temp_x = xpos + i
            temp_y = ypos
        if direction == 1:
            temp_x = xpos
            temp_y = ypos + i

        #check the tile can be placed on
        check_ret = map_place_ship_tile_validate(map_arr_copy, temp_x, temp_y, \
                                                 dim_x, dim_y)
        #If tile placement is valid
        if check_ret == 1:
            map_arr_copy[temp_x][temp_y] = 'T'
        else:
            return 1 #can't place ship here

    #checking done, convert map copy as real map
    for i in range(dim_x):
        for j in range(dim_y):
            if (map_arr_copy[i][j] == 'T'):
                map_arr[i][j] = 'S'

    return 0 #placed ship successfully


#respond to attacks coming over socket
#return: -1 on miss, -2 on hit, -3 on win + Coordinates of attack.
def map_manage_attack(map_arr, dim_x, dim_y, sock):
    
    ret = game.safe_recv(sock)
    ret = ret.split(',')
    ret[0] = int(ret[0]) #X of attack
    ret[1] = int(ret[1]) #Y of attack
    
    if map_arr[ret[0]][ret[1]] == '-': #if miss
        map_arr[ret[0]][ret[1]] = 'm'
        game.safe_send(sock, '-')
        return -1, ret[0], ret[1]

    elif map_arr[ret[0]][ret[1]] == 'S': #if hit
        map_arr[ret[0]][ret[1]] = 'X'
        
        if game.check_win(map_arr, dim_x, dim_y) == 1: #check win
            game.safe_send(sock, 'W')
            return -3, ret[0], ret[1]
        else:
            game.safe_send(sock, 'S')
            return -2, ret[0], ret[1]


#relic name, send attacks to opponent, return outcome
#return: 1 on fail, -1 on miss, -2 on hit, -3 on win
def map_place_attack(map_arr, xpos, ypos, dim_x, dim_y, sock):
    
    if 0 <= xpos < dim_x and 0 <= ypos < dim_y:
        if map_arr[xpos][ypos] == 'm' or map_arr[xpos][ypos] == 'X':
            return 1
        else:
            buf = str(xpos)+','+str(ypos)
            game.safe_send(sock, buf)
            ret = game.safe_recv(sock)
            
            if ret == '-':
                map_arr[xpos][ypos] = 'm'
                return -1
            elif ret == 'S':
                map_arr[xpos][ypos] = 'X'
                return -2
            elif ret == 'W':
                return -3
            else:
                game.exit_unexpected()
    else:
        return 1


#create empty map
#used to create 2d arrays for maps
def fill_array(arr, arr_size, value, value_is_arr):
    
    for i in range(0, arr_size):
        if value_is_arr:
            arr.append(copy.deepcopy(value))
        else:
            arr.append(value)


#create empty map
#return: size_x and size_y actually used
def map_generate(map_arr, size_x, size_y):
    
    CONST_LOW_BOUND = 9
    CONST_HIGH_BOUND = 12

    y_arr = []

    '''
    Creates and returns array of size [size_x][size_y].
    If size_x OR size_y are 0, randomly determines size in range 8-12.
   
    '''

    #if not used now, used later
    random.seed(datetime.now())

    #determine map dimensions
    if (CONST_LOW_BOUND <= size_x <= CONST_HIGH_BOUND) and \
       (CONST_LOW_BOUND <= size_y <= CONST_HIGH_BOUND):
        print("Generating map...")
    else:
        print("Map dimensions do not fall into range 9 to 12, "\
              "generating own dimensions.")
        size_x = random.randint(CONST_LOW_BOUND, CONST_HIGH_BOUND)
        size_y = random.randint(CONST_LOW_BOUND, CONST_HIGH_BOUND)
        print("New dimensions: X: ", size_y, "Y: ", size_x);
    
    #initialising empty map
    fill_array(y_arr, size_y, '-', False)
    fill_array(map_arr, size_x, y_arr, True)

    return size_x, size_y


def test():
    x = []
    map_generate(x, 8, 7)
    print(x)
