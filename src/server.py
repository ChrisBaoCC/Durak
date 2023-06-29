#!usr/bin/env python3
"""
`server` module. Contains the `Server` class.
Credit goes to this website
https://www.techwithtim.net/tutorials/python-online-game-tutorial/connecting-multiple-clients/
for providing a lot of the code for the `server` and `client` modules.
"""

__author__ = "Chris Bao"
__version__ = 0.9

### Imports ###
import socket as s
from _thread import *
from game import Game, Player


class Server:
    """
    `Server` class. Provides methods for running the server.
    """

    ### Constants ###
    IP: str = ""
    """Set to the IP address of whoever's running the server,
    or '' for all connections."""
    PORT: int = 6666
    """Connection port number. Pretty much arbitrary."""
    BUFFER_SIZE: int = 4096
    """Size of buffer for receiving messages."""
    MAX_PLAYERS: int = 6
    """Maximum number of players per game."""

    ### Instance variables ###
    socket: s.socket
    """The `socket` that the server uses to connect."""
    player_count: int
    """Number of players connected."""
    ready_count: int
    """Number of players who have confirmed ready."""
    client_sockets: list[s.socket]
    client_addresses: list[tuple[str, int]]
    """List of (address, port) for clients."""
    players: list[Player]
    """List of players."""

    def __init__(self) -> None:
        """
        Constructor. Initializes the server.

        Parameters
        ---
        (no parameters)

        Returns
        ---
        `None`
        """
        self.socket: s.socket = s.socket(
            s.AF_INET, s.SOCK_STREAM)

        try:
            self.socket.bind((Server.IP, Server.PORT))
        except s.error as err:
            print(str(err))

        self.player_count: int = 0
        self.ready_count: int = 0

        self.client_sockets: list[s.socket] = []
        self.client_addresses: list[tuple[str, int]] = []
        self.players: list[Player] = []

        self.socket.listen(Server.MAX_PLAYERS)
        print("Server initialized. Waiting for up to " +
              f"{Server.MAX_PLAYERS} connections...")

    def threaded_client(self, client: s.socket, player_index: int) -> None:
        """
        Run the connection to the client.

        Parameters
        ---
        `client: socket` - the socket to the client
        `player_index: int` - the index of the `Player` instance
                              assigned to the client within self.players

        Returns
        ---
        `None`
        """
        client.send(str.encode("player: " + str(self.players[player_index])))

        while True:
            try:
                message = client.recv(4096).decode()

                if message == "ready":
                    self.ready_count += 1
                    print(f"Player {player_index} is ready!")

                print("received message:", message)

                # if message == "message":
                #     # do something
                #     pass

                client.send(str.encode("received"))
            except Exception as e:
                print(f"Error reading input from player {player_index}:",
                      str(e) + ".")
                break

        print(
            f"Lost connection to player {player_index}, closing connection.")
        client.close()

    # TODO: figure out when/how to start the game
    # TODO: figure out how to restart when a player leaves

    def mainloop(self) -> None:
        """
        Keep the server running.

        Parameters
        ---
        (no parameters)

        Returns
        ---
        `None`
        """
        while True:
            socket, address = self.socket.accept()
            self.client_sockets.append(socket)
            self.client_addresses.append(address)
            print(f"Connected to player {self.player_count}:",
                  address[0], "at", str(address[1])+".")

            new_player = Player()
            self.players.append(new_player)
            self.player_count += 1

            # self.player_count-1 is the index of the player
            start_new_thread(self.threaded_client,
                             (socket, self.player_count-1))


def main() -> None:
    """
    Run everything.

    Parameters
    ---
    (no parameters)

    Returns
    ---
    `None`
    """
    server = Server()
    server.mainloop()


if __name__ == "__main__":
    main()
