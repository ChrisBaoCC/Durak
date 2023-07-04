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
from threading import Lock
from collections import deque
import pygame
from card import Card
from game import Game, Player


class Server:
    """
    `Server` class. Provides methods for running the server.
    """

    ### Constants ###
    IP: str = ""
    """Set to the IP address of whoever's running the server,
    or '' for all connections."""
    PORT: int = 6667
    """Connection port number. Pretty much arbitrary."""
    BUFFER_SIZE: int = 4096
    """Size of buffer for receiving messages."""
    MAX_PLAYERS: int = 6
    """Maximum number of players per game."""

    ##################################
    # THIS MUST BE SET EVERY GAME!!! #
    ##################################
    DESIRED_PLAYERS: int = 1
    """Set by the host. Number of people to wait for before the game can start."""

    # State constants
    STATE_START: int = 0
    STATE_WAIT: int = 1
    STATE_PLAY: int = 2
    STATE_END: int = 3

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
    state: int
    """Tracks game state. See state constants for more info."""
    lock: Lock
    """Lock on the game state to avoid issues while multithreading."""
    game: Game
    """The game instance."""

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

        pygame.init()
        # we don't care about the actual display;
        # display just needs to be created so that card images can be loaded
        # so that we don't get an error initializing the game
        pygame.display.set_mode(flags=pygame.HIDDEN)
        Card.load_images()

        self.player_count: int = 0
        self.ready_count: int = 0

        self.client_sockets: list[s.socket] = []
        self.client_addresses: list[tuple[str, int]] = []
        self.players: list[Player] = []
        self.state = Server.STATE_START

        self.lock = Lock()
        self.game = None

        self.socket.listen(Server.MAX_PLAYERS)
        print("Server initialized. Waiting for up to " +
              f"{Server.MAX_PLAYERS} connections...")

    def start_game(self) -> None:
        """
        Everyone is ready, initialize the game.

        Parameters
        ---
        (no parameters)

        Returns
        ---
        `None`
        """
        print("All players are ready! Starting game...")
        self.state = Server.STATE_PLAY
        self.lock.acquire()

        # make sure we don't re-initialize the game
        if self.game is not None:
            self.lock.release()
            return

        self.game = Game(self.players)
        self.lock.release()

    def generate_message(self, input: str, player_index: int) -> str:
        """
        Generate the update message to send back over the specified
        connection.

        Parameters
        ---
        `input: str` - message given by client.
        `player_index: int` - player id.

        Returns
        ---
        `str` - message.
        """
        match input:
            case "start":
                return "start"
            case "wait" | "ready":
                return "wait" + " " + str(self.ready_count) + " " + str(Server.DESIRED_PLAYERS)
            case "play":
                # TODO: this has to give more information about game state
                self.lock.acquire()
                result = "play " + str(self.players[player_index])
                self.lock.release()
                return result
            case "end":
                return ""  # TODO

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
        client.send(str.encode(str(self.players[player_index])))

        to_do = deque()
        while True:
            try:
                message = client.recv(4096).decode()

                if message == "ready":
                    self.ready_count += 1
                    print(f"Player {player_index} is ready!")
                    if self.ready_count == Server.DESIRED_PLAYERS:
                        to_do.appendleft("start game")

                # DEBUG
                # if message != "refresh":
                #     print("received message:", message)

                reply = str.encode(
                    self.generate_message(message, player_index))
                # DEBUG
                # print(self.state, reply)
                client.send(reply)
            except Exception as e:
                print(f"Error reading input from player {player_index}:",
                      str(e) + ".")
                break

            while len(to_do) > 0:
                task = to_do.popleft()
                if task == "start game":
                    self.start_game()

        print(
            f"Lost connection to player {player_index}, closing connection.")
        client.close()

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
        try:
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

                if self.player_count == Server.DESIRED_PLAYERS:
                    print("All players have joined! Waiting for players to ready...")
                    self.state = Server.STATE_WAIT
        except:
            pass
        finally:
            print("Closing socket...")
            self.socket.close()


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
