from SmartSocket import connections
Event = connections.BasicEvent

SERVER_ADDRESS = (connections.getLocalIP(), 7871)

SERVER = connections.SERVER(SERVER_ADDRESS)
system = connections.ServerClientSystem(SERVER)
print("Server:",system.server)
print(f"Hosting on: {SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}")

server_running = True

player_turn = 1
# player 1 or 2's turn

game_running = False

player_1_ready = False
player_2_ready = False

player_1_client = None
player_2_client = None

board = [
    [0,0,0],
    [0,0,0],
    [0,0,0]
]

while server_running:

    new_clients, new_messages, disconnected = system.main()

    for new_client in new_clients:
        conn, addr = new_client
        if player_1_client is None:
            player_1_client = new_client
        elif player_2_client is None:
            player_2_client = new_client
        else:
            conn.close()
            system.remove_client(conn)

    for msg in new_messages:
        if msg.is_dict:
            msg_o = Event(msg)
            print(f"New message {str(msg_o.event)}")

            event = msg_o.event
            from_c = msg_o.from_conn

            if msg_o.is_i('ready'):
                if from_c == player_1_client[0]:
                    player_1_ready = True
                    system.send_to_conn(player_1_client[0], Event('ok'))
                elif from_c == player_2_client[0]:
                    player_2_ready = True
                    system.send_to_conn(player_2_client[0], Event('ok'))
                
                if player_1_ready and player_2_ready:
                    # start the game
                    print("Server ready to start game, 2 players are connected")
                    system.send_to_clients(Event('start'))
            
            elif msg_o.is_i('click_tile'):
                coord = msg_o.get('coord')
                if coord is not None:
                    player_index = 1 if msg_o.from_conn == player_1_client[0] else 2
                    if player_turn == player_index:
                        # allow the player to make a turn
                        if board[coord[1]][coord[0]] == 0:
                            board[coord[1]][coord[0]] = player_index
                            system.send_to_clients(Event('update_board', coord=coord, value=player_index))
                            if player_turn == 1: player_turn = 2
                            else: player_turn = 1
                            print(f"move made, it is now player {player_turn}'s turn")

        else:
            print(f"New message: is_dict:{msg.is_dict}, is_pickled:{msg.is_pickled}")

    for client in disconnected:
        print(f"Client disconnected {client[1][0]}:{client[1][1]}")