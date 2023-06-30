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
from card import Card

pygame.freetype.init()


class Client:
    """
    `Client` class. Provides user interface and network functionality.
    """

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

    BG_COLOR: tuple[int, int, int] = (0, 0, 0)
    BTN_BG_COLOR: tuple[int, int, int] = (255, 255, 255)
    BTN_FG_COLOR: tuple[int, int, int] = (0, 0, 0)

    READY_BTN_WIDTH: int = 200
    READY_BTN_HEIGHT: int = 80

    # State constants
    STATE_START: int = 0
    STATE_WAIT: int = 1
    STATE_PLAY: int = 2
    STATE_END: int = 3

    ### Instance variables ###
    socket: s.socket
    """Socket that handles the connection to the server."""
    player: Player
    """Represents the player's hand."""
    clock: pygame.time.Clock
    """Timer for game refresh."""
    window: pygame.Surface
    """Window that holds the UI."""

    state: int
    """Tracks state of game. See state constants for more info."""

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

        Card.load_images()

        self.state = Client.STATE_START
        self.button = self.Button(self.window,
                                  "Ready!",
                                  (self.WINDOW_WIDTH/2 - self.READY_BTN_WIDTH/2,
                                   self.WINDOW_HEIGHT/2 - self.READY_BTN_HEIGHT/2),
                                  (self.READY_BTN_WIDTH, self.READY_BTN_HEIGHT),
                                  self.BTN_FG_COLOR,
                                  self.BTN_BG_COLOR,
                                  self.Button.BUTTON_FONT)

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

    def draw(self) -> None:
        """
        Draw everything to the window.

        Parameters
        ---
        (no parameters)

        Returns
        ---
        `None`
        """
        self.window.fill(Client.BG_COLOR)

        self.button.draw()

        # use the correct cursor
        # selecting button
        if self.button.check_hover():
            pygame.mouse.set_cursor(
                pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND))
        # default arrow
        else:
            pygame.mouse.set_cursor(
                pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW))

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
            self.clock.tick(60)
            # self.clock.tick(30)  # temporary, to reduce the number of messages

            message = "refresh"

            # handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONUP:
                    if self.button.check_hover():
                        self.button.visible = False
                        message = "ready"
                        self.state = Client.STATE_WAIT

            # user_input = input("input here: ")
            # thing = self.send_request(user_input)

            thing = self.send_request(message)
            # TODO: debug print statement
            if thing != "received":
                print(thing)

            # draw things
            self.draw()
            pygame.display.update()

    class Button:
        """
        `Button` inner class for the UI.
        """

        BUTTON_FONT: pygame.freetype.Font = pygame.freetype.Font(
            "../res/font/robotoRegular.ttf", 48)

        def __init__(self, window: pygame.Surface, text: str, pos: tuple[int, int],
                     size: tuple[int, int], fg: tuple[int, int, int],
                     bg: tuple[int, int, int], font: pygame.freetype.Font) -> None:
            """
            Constructor.

            Parameters
            ---
            `window: pygame.Surface` - window this belongs to (is drawn on).
            `text: str` - button text.
            `pos: tuple[int, int]` - position of the button on the window.
            `size: tuple[int, int]` - width and height.
            `fg: tuple[int, int, int]` - RGB color of the text.
            `bg: tuple[int, int, int]` - RGB color of the background.

            Returns
            ---
            `None`
            """
            self.window: pygame.Surface = window
            self.text: str = text
            self.pos: tuple[int, int] = pos
            self.size: tuple[int, int] = size
            self.rect: pygame.Rect = pygame.Rect(*self.pos, *self.size)
            self.fg: tuple[int, int, int] = fg
            self.bg: tuple[int, int, int] = bg
            self.font: pygame.font.Font = font
            self.visible: bool = True

        def draw(self):
            """
            Draw this button.

            Parameters
            ---
            (no parameters)

            Returns
            ---
            `None`
            """
            if not self.visible:
                return

            fg = self.fg
            bg = self.bg

            # draw box
            # reverse colors when hovered
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                fg = self.bg
                bg = self.fg
            button_rect = pygame.draw.rect(self.window, bg, self.rect)
            # add outline when hovered
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.window, fg, self.rect, width=2)

            # draw text
            text_surface = self.font.render(
                self.text, fg, bg)[0]
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.window.blit(text_surface, text_rect)

        def check_hover(self) -> bool:
            """
                Check if this button has been clicked.

                Parameters
                ---
                (no parameters)

                Returns
                ---
                `bool` - `True` if clicked, `False` otherwise
                """
            return self.visible and self.rect.collidepoint(pygame.mouse.get_pos())


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
