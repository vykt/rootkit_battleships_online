# draw.py

import sys


'''
Most functions inside draw.py are wrappers for print. This prevents
code from becoming bloated from long print statements. it also allows
large, significant print statements to be modified all in one place.

'''


#Pretty print map with axis and heading.
def print_map(map_arr, dim_x, dim_y, map_type): 

    #Dimensions reversed, x = vert, y = horiz.

    #False = enemy, True = ally
    if map_type:
        print("\n\tAlly Map\n")
    else:
        print("\n\tEnemy Map\n")

    buffer = ""
    sys.stdout.write("   ")
    for i in range(dim_y):
        buffer = buffer + chr(ord('A')+i) + " "
    print(buffer)
    for i in range(dim_x):
        buffer = str(i) + " "
        if i < 10:
            buffer = buffer + " "
        sys.stdout.write(buffer)
        for j in range(dim_y):
            #Potentially hiding enemy ships from appearing on the map
            if not map_type and map_arr[i][j] == 'S':
                buffer = '-' + " "
            else:
                buffer = map_arr[i][j] + " "
            sys.stdout.write(buffer)
        sys.stdout.write('\n')


#Midgame menu.
def print_game_menu():

    print('''
    BATTLESHIPS
     game menu

Welcome to the game. Both you and your
opponent have now placed your ships down.
Below is the value of each tile and what it
means:

    '-' : Empty(?) tile.

    'S' : Ship present.

    'X' : Ship hit.

    'm' : Missed shot.

You may attack any tile you have not attacked
so far. This means tiles with 'm' and 'X' can't
be attacked again.

The game takes place in turns with the host
starting first. After making your move, please
wait for your opponent to make their move.

Use the following commands to play the game:

    >attack <X> <Y> -Attack a square. Example:
                            "attack C 7"

    >map_ally       -Display your own map.

    >map_enemy      -Display enemy map.

    >menu           -Show this message again.

    >quit           -Quit the game.

''')


#Ship placement menu.
def print_init_game_menu_placeships():

    print('''
    BATTLESHIPS ONLINE
     place your ships!

You can now proceed to place your ships on the
map. Note that depending on orientation, ships
will be placed either south or west from the
first tile they are placed on. For example, a
vertically oriented placement of a ship of size
3 placed on A 3 will occupy tiles A 3, A 4 and
A 5. Note also that ships can't be placed
directly adjascent to one another, they may only
be placed diagonally adjascent to each other. 
Ships are placed in order, largest first.

If you have finished placing your ships, you may
need to wait for your opponent to finish placing
theirs before the game can proceed.

To place ships, use the following commands:

    >place <X> <Y>  -Place the ship. Example:
                            "place B 4"

    >orientation    -Switch between placing
                     ships facing horizontally
                     or vertically.

    >list_ships     -Show each ship and its size.

    >menu           -Show this message again.

    >map            -Show current state of map.

    >quit           -Quit the game.

''')


#List ships nicely, as well as tag the currently placed ship.
def print_init_game_ships(ship_names_temp, ship_temp, index):
    
    for i in range(len(ship_names_temp)):
        buf = str(ship_names_temp[i]) + " " + str(ship_temp[i])
        if i == index:
            buf = buf + ' X'
        buf = buf + '\n'
        sys.stdout.write(buf)
    print("")


#Menu for initialising the game.
def print_init_game_menu(is_host):

    if is_host:
        print('''
    BATTLESHIPS ONLINE
         init game

Please provide dimensions for the map,
between 9 and 12. If you provide values
outside this range, new ones will be generated
for you.

''')

    else:
        print('''

    BATTLESHIPS ONLINE
         init game

Please wait for the host to generate the map
and send it to you.

''')


#Menu for connecting to other players.
def print_connection_menu():

    print('''
    BATTLESHIPS ONLINE
       host or join

Please choose to either host a game or join one.
You will be asked to enter the address of the
person you wish to connect to / listen for. You
will also be asked to provide a port. If you're
unsure of what port to use, consider using '2929'.

As host, you may enter '0.0.0.0' to listen for
any incoming connection. 

    >host           - Host a game.

    >join           - Join a game.

    >quit           - Quit game.

''')


#Main menu, including its help command.
def print_main_menu(help=False):
    
    if not help:
        print('''
    BATTLESHIPS ONLINE
         main menu

Welcome to Battleships Online. Please consult the
player guide.

Enter one of the following options to continue:

    >play           - Play online against an oponent.
    
    >help           - Show some helpful information.
    
    >menu           - Show this menu again.
    
    >quit           - Exit the script.

''')
    else:
        print('''
Navigate the game menues and play the game by entering
options into the command prompt below. The menu will
let you proceed once you provide it with a correct
option. If you mistype or provide an incorrect option,
you will be re-prompted to provide input until a valid
option is provided.

In Battleships Online, you get the choice of hosting or
joining a hosted game. The host determines the map
dimensions and has the first move.

''')


