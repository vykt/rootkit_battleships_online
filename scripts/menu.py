# menu.py

import sys
import copy
import socket

import map
import draw
import game


'''
All user interaction occurs here. Substantial changes from offline
version. Namely, player-sided functionality of player.py pulled here.
Inclusion of networking also made this more clumsy.
'''


'''
The get_sanitised_input() function handles almost every input required
by Battleships. The caller is only required to call the function once
to get completely a valid input. "extend_opt" argument causes the
function to validate complex input and pass it on to its relevant
function before returning. These 2 different types of input
have to be combined because users can choose to attack or do another,
simple function. Hence have to check for both at once.

options     = Every possible regular input of a menu, used by menues.

extend_opt = Integer index for the "attack" and "place" inputs. These 
are predefined inside the function.

              1 - "attack", 2 - "place" 

extend_opt 1 (attack): return -1 on ship miss, -2 on ship hit
extend_opt 2 (place):  return -1 on successful placement

'''
#returns: index of option, -1 on ship miss, -2 on ship hit
#                          -1 on ship placed successfully
def get_sanitised_input(options, extend_opt=0, map_arr=0, dim_x=0, dim_y=0,\
                        ship_template=0, ship=0, direction=0, sock=0):

    while True:
        inp = ""
        #first check for regular options
        inp = str(input("> "))
        for i in range(len(options)):
            if inp.lower() == options[i]:
                return i
        if dim_x == 0 : #check if ingame input needs testing
            continue
        
        #now check for game options
        extend_opt_arr = ("NULL","attack", "place")
        tgt_x = -1
        tgt_y = -1
        ret = 0
        inp = inp.lower()
        inp = inp.split()
        if inp[0] == extend_opt_arr[extend_opt]:
            try:
                tgt_x = int(ord(inp[1])) - 97 #convert to ascii, then a = 0
                tgt_y = int(inp[2])
            except:
                continue

            if extend_opt == 1: #"attack"
                ret = map.map_place_attack(map_arr, tgt_y, tgt_x, dim_x, dim_y, sock)
                if ret == 1:
                    continue
                else:
                    return ret
            if extend_opt == 2: #"place"
                ret = map.map_place_ship(map_arr, ship_template, ship, direction,\
                                         tgt_y, tgt_x, dim_x, dim_y)
                if ret == 1:
                    continue
                else:
                   return -1


#getting savefile input behaves differently, hence requiring own function.
def get_sanitised_file(do_read=False):
    
    #Please don't chmod a-r ./* :)
    while True:
        inp = str(input("filename > "))
        if do_read:
            try:
                file = open(inp, "r")
                file.close()
                return inp
            except:
                continue
        else:
            try:
                file = open(inp, "w")
                file.close()
                return inp
            except:
                continue


#integers, once again differ from regular input.
def get_sanitised_map_size():
    
    dim_name = ('X', 'Y')
    dim = []

    for i in range(2):
        while True:
            buf = "size " + dim_name[i] + " > "
            try:
                inp = int(input(buf))
                dim.append(inp)
                break
            except:
                continue

    return dim[1], dim[0]


#checking address is within ipv4 standard.
#return: 0 - valid, 1 - fail
def validate_address(address):
    addr = address.split('.')
    if len(addr) != 4:
        return 1
    for i in range(4):
        try:
            seg = int(addr[i])
            if not (0 <= seg <= 255):
                return 1
        except:
            return 1
    return 0


#checking port is within real range.
#return: 0 - valid, 1 - fail
def validate_port(port):
    try:
        int_port = int(port)
        if not (0 <= int_port <= 65536):
            return 1
    except:
        return 1
    return 0


#networked addition, gets IP and port.
#return: ip, port
def get_sanitised_address_port():

    address = ""
    port = -1

    while True:
        try:
            address = str(input("Address (ipv4): > "))
            if validate_address(address) == 0:
                break
        except:
            continue

    while True:
        try:
            port = str(input("Port: > "))
            if validate_port(port) == 0:
                break
        except:
            continue
    return address, int(port)


#midgame menu
def game_menu(map_arr, enemy_map_arr, size_x, size_y, is_host, sock):

    game_opts = ("map_ally", "map_enemy", "menu", "quit")
    draw.print_game_menu()

    if not is_host: #host goes first
        game.handle_attack(map_arr, size_x, size_y, sock)

    print("Your turn. 'menu' to show options.")
    while True:
        inp = get_sanitised_input(options=game_opts, extend_opt=1,\
                                  map_arr=enemy_map_arr,\
                                  dim_x=size_x, dim_y=size_y, sock=sock)

        if inp == 0: #map_ally
            draw.print_map(map_arr, size_x, size_y, True)
            continue
        
        elif inp == 1: #map_enemy
            draw.print_map(enemy_map_arr, size_x, size_y, False)
            continue
        
        elif inp == 2: #menu
            draw.print_game_menu()
            continue
        
        elif inp == 3: #quit
            game.exit_normal()
            
        elif inp == -1: #ship miss
            print("Missed!")

        elif inp == -2: #ship hit
            print("Ship hit!")

        elif inp == -3: #win
            draw.print_map(map_arr, size_x, size_y, True)
            draw.print_map(enemy_map_arr, size_x, size_y, False)
            print("\nCongratulations! You win!")
            sock.close()
            game.exit_normal()

        game.handle_attack(map_arr, size_x, size_y, sock)
        

#init game
def init_game_menu(map_arr, enemy_map_arr, ship_temp, ship_names_temp, is_host,\
                   sock):
    
    size_x = -1
    size_y = -1

    init_opts = ("orientation", "list_ships", "menu", "map", "quit")
    direction = -1 #-1 = south, 1 = west
    direction_names = ("NULL", "west", "south")

    #draw initial empty maps
    draw.print_init_game_menu(is_host)

    #host sets mapsize
    if is_host:
        size_x, size_y = get_sanitised_map_size()
        size_x, size_y = map.map_generate(map_arr, size_x, size_y)
        buf = str(size_x)+','+str(size_y)
        game.safe_send(sock, buf)

    #joined receives mapsize
    else:
        recv_buf = game.safe_recv(sock)
        recv_buf = recv_buf.split(',')
        size_x = int(recv_buf[0])
        size_y = int(recv_buf[1])
        map.map_generate(map_arr, size_x, size_y)
    enemy_map_arr = copy.deepcopy(map_arr)

    #place player's ships
    draw.print_init_game_menu_placeships()
    for i in range(len(ship_temp)):
        while True:
            print("Placing ship: ", ship_names_temp[i], " (",ship_temp[i],") "\
                  "Oriented: ", direction_names[direction]);
            inp = get_sanitised_input(options=init_opts, extend_opt=2,\
                                      map_arr=map_arr, dim_x=size_x,\
                                      dim_y=size_y, ship_template=ship_temp,\
                                      ship=i, direction=direction)

            if inp == 0: #orientation
                direction = direction * -1
                print("Changed orientation")
        
            elif inp == 1: #list_ships
                draw.print_init_game_ships(ship_names_temp, ship_temp, i)

            elif inp == 2: #menu
                draw.print_init_game_menu_placeships()

            elif inp == 3: #map
                draw.print_map(map_arr, size_x, size_y, True)

            elif inp == 4: #quit
                game.exit_normal()
        
            elif inp == -1: #ship placed
                break
    
    game.safe_send(sock, "place_done")
    print("Waiting for opponent...")
    recv_buf = game.safe_recv(sock)
    
    if recv_buf == "place_done":
        game_menu(map_arr, enemy_map_arr, size_x, size_y, is_host, sock)

    else:
        sock.close()
        game.exit_unexpected()


#choose to host or join, handle each
def connection_menu(map_arr, enemy_map_arr, ship_temp, ship_names_temp):

    draw.print_connection_menu()

    conn_opts = ("host", "join", "quit")
    conn_type = get_sanitised_input(conn_opts)
    if conn_type == 2:
        game.exit_normal()
    addr, port = get_sanitised_address_port()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if conn_type == 0: #host
        try:
            sock.bind((addr, port))
        except:
            print("Unable to host on this address and port.")
            game.exit_normal()

        sock.listen(1)
        print("Waiting for opponent...")
        enemy_sock, enemy_addr = sock.accept()
        sock.close()
        #launch menu with is_host True
        init_game_menu(map_arr, enemy_map_arr, ship_temp, ship_names_temp,\
                       True, enemy_sock)

    elif conn_type == 1: #join
        try:
            sock.connect((addr, port))
        except:
            print("There are no hosts available at this address and port.")
            game.exit_normal()
        #launch menu with is_host False 
        init_game_menu(map_arr, enemy_map_arr, ship_temp, ship_names_temp,\
                       False, sock)
    else:
        game.exit_unexpected()


#main, starting menu
def main_menu():
   
    ship_template = [5, 4, 3, 3, 2, 2]
    ship_names_template = ["Aircraft Carrier", "Battleship", "Destroyer",\
                           "Cruiser", "Submarine", "Patrol Boat"]

    player_map_arr = []
    enemy_map_arr = []
    #sizes defined later

    draw.print_main_menu()

    options_tuple = ("play", "help", "menu", "quit")
    
    while True:

        ret = get_sanitised_input(options_tuple)

        if ret == 0: #play
            connection_menu(player_map_arr, enemy_map_arr, ship_template,\
                           ship_names_template)
        
        elif ret == 1: #help
            draw.print_main_menu(help=True)
        
        elif ret == 2: #menu
            draw.print_main_menu()
        
        elif ret == 3: #quit
            game.exit_normal()

main_menu()
