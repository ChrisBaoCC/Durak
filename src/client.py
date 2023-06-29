#!usr/bin/env python3
"""`client` module. Provides the `Client` class.
Credit goes to this website
https://www.techwithtim.net/tutorials/python-online-game-tutorial/connecting-multiple-clients/
for providing a lot of the code for the `server` and `client` modules.
"""

### Imports ###
# External imports
import socket as s
import pygame
import pygame.freetype
from pygame.locals import *
import sys

# Internal imports
from game import Player


class Client:
    """
    `Client` class. Provides user interface and network functionality.
    """

    class Button:
        """
        `Button` class for the UI.
        """

        BUTTON_FONT: pygame.freetype.Font = pygame.freetype.Font(
            "../res/font/robotoRegular.ttf", 48)

        def __init__(self, text: str, pos: tuple[int, int], size: tuple[int, int],
                     fg: tuple[int, int, int], bg: tuple[int, int, int],
                     font: pygame.freetype.Font) -> None:
            """
            Constructor.

            Parameters
            ---
            `text: str` - button text.
            `pos: tuple[int, int]` - position of the button on the window.
            `size: tuple[int, int]` - width and height.
            `fg: tuple[int, int, int]` - RGB color of the text.
            `bg: tuple[int, int, int]` - RGB color of the background.

            Returns
            ---
            `None`
            """
            self.text: str = text
            self.pos: tuple[int, int] = pos
            self.size: tuple[int, int] = size
            self.fg: tuple[int, int, int] = fg
            self.bg: tuple[int, int, int] = bg
            self.font: pygame.font.Font = font

        def draw(self, window: pygame.Surface):
            """
            Draw this button to the specified window.

            Parameters
            ---
            `window: pygame.Surface` - window to draw on.

            Returns
            ---
            `None`
            """
            # TODO: check this works
            button_rect = pygame.draw.rect(
                window, self.bg, self.pos + self.size)
            text_surface = self.font.render(self.text, True, self.fg)
            text_rect = text_surface.get_rect(center=button_rect.center)
            window.blit(text_surface, text_rect)

        def check_clicked(self, mouse_x: int, mouse_y: int) -> bool:
            """
            Check if this button has been clicked given a mouse position.

            Parameters
            ---
            `mouse_x: int`
            `mouse_y`: int`

            Returns
            ---
            `bool` - `True` if clicked, `False` otherwise
            """
            return (self.pos[0] <= mouse_x <= self.pos[0] + self.size[0] and
                    self.pos[1] <= mouse_y <= self.pos[1] + self.size[1])

        # TODO: add and check button

    ### Constants ###
    # For IO
    IP: str = "127.0.0.1"  # "71.184.230.103"
    """Set to the IP address of whoever's running the server."""
    PORT: int = 6666
    """Connection port number. Pretty much arbitrary."""
    BUFFER_SIZE: int = 4096
    """Size of buffer for receiving messages."""

    # For UI
    WINDOW_WIDTH: int = 1440
    WINDOW_HEIGHT: int = 900

    ### Instance variables ###
    socket: s.socket
    """Socket that handles the connection to the server."""
    player: Player
    """Represents the player's hand."""
    clock: pygame.time.Clock
    """Timer for game refresh."""
    window: pygame.Surface
    """Window that holds the UI."""

    def __init__(self) -> None:
        """
        Constructor.

        Parameters
        ---
        (no parameters)

        Returns
        ---
        `None`
        """
        self.socket: s.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.player: Player = Player(self.connect())

        pygame.init()
        pygame.display.set_caption("Durak!")
        pygame.display.set_icon(pygame.image.load("../res/icon/appicon.png"))
        self.window: pygame.Surface = pygame.display.set_mode(
            (Client.WINDOW_WIDTH, Client.WINDOW_HEIGHT))
        self.clock: pygame.time.Clock = pygame.time.Clock()

    def connect(self) -> str:
        """
        Connect to the server.

        Parameters
        ---
        (no parameters)

        Returns
        ---
        `str` - message from the server.
        """
        try:
            self.socket.connect((Client.IP, Client.PORT))
            return self.socket.recv(Client.BUFFER_SIZE).decode()
        except Exception as e:
            print(e)

    def send_request(self, message: str) -> str:
        """
        Send data to and request data from the server.

        Parameters
        ---
        `message: str` - message to send to the server.

        Returns
        ---
        `str` - data received.
        """
        try:
            self.socket.send(str.encode(message))
            return self.socket.recv(Client.BUFFER_SIZE).decode()
        except s.error as e:
            print(e)

    def mainloop(self) -> None:
        """
        Mainloop. Handle all events while the app is running.

        Parameters
        ---
        (no parameters)

        Returns
        ---
        `None`
        """
        while True:
            # handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            # user_input = input("input here: ")
            # thing = self.send_request(user_input)

            self.clock.tick(60)
            thing = self.send_request("refresh")

            print(thing)


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
    client = Client()
    client.mainloop()


if __name__ == "__main__":
    main()
