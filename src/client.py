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
import pygame.mixer
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
    PORT: int = 6667
    """Connection port number. Pretty much arbitrary."""
    BUFFER_SIZE: int = 4096
    """Size of buffer for receiving messages."""

    # For UI
    WINDOW_WIDTH: int = 1440
    WINDOW_HEIGHT: int = 900

    MEDIUM_FONT: pygame.freetype.Font = pygame.freetype.Font(
        "../res/font/robotoRegular.ttf", 48)

    BG_COLOR: tuple[int, int, int] = (0, 0, 0)
    BOX_BG_COLOR: tuple[int, int, int] = (255, 255, 255)
    BOX_FG_COLOR: tuple[int, int, int] = (0, 0, 0)

    BOX_PADDING: int = 30  # space between text and edge

    CARD_OFFSET: int = 40  # offset between cards in hand
    CARD_YPOS: int = 600
    CARD_YLIFT: int = 100  # amount card moves up by when selected

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
    """Tracks whether mouse is hovering over a button or not."""
    announcement: str
    """Holds any big messages to display."""
    announcement_sticky: bool
    """Toggle for whether announcement will persist between refreshes."""

    flip_sound: pygame.mixer.Sound
    tap_sound: pygame.mixer.Sound

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

        pygame.mixer.init()
        self.flip_sound = pygame.mixer.Sound("../res/sound/flip.wav")
        self.flip_sound.set_volume(0.5)
        self.tap_sound = pygame.mixer.Sound("../res/sound/tap.wav")
        self.tap_sound.set_volume(0.5)

        Card.load_images()

        self.state: int = Client.STATE_START
        self.mouse_hovering: bool = False
        self.button: Client.Button = self.Button(self.window,
                                                 "I'm ready!",
                                                 (self.WINDOW_WIDTH/2,
                                                  self.WINDOW_HEIGHT/2),
                                                 self.BOX_FG_COLOR,
                                                 self.BOX_BG_COLOR,
                                                 self.MEDIUM_FONT)

        self.announcement: str = ""
        self.announcement_sticky = False

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

    def draw_announcement(self) -> None:
        """
        Draw announcement box.

        Parameters
        ---
        (no parameters)

        Returns
        ---
        `None`
        """
        if self.announcement == "":
            return

        fg = self.BOX_FG_COLOR
        bg = self.BOX_BG_COLOR

        text_surface, text_rect = Client.MEDIUM_FONT.render(
            self.announcement, fg, bg)
        box_rect: pygame.Rect = text_rect.copy()
        box_rect.inflate_ip(Client.BOX_PADDING, Client.BOX_PADDING)
        box_rect.center = (Client.WINDOW_WIDTH/2, Client.WINDOW_HEIGHT/2)
        pygame.draw.rect(self.window, bg, box_rect,
                         border_radius=int(box_rect[3]/5))
        text_rect.center = box_rect.center
        self.window.blit(text_surface, text_rect)

    def draw_cards(self) -> None:
        """
        Draw the cards held by the player.

        Parameters
        ---
        (no parameters)

        Returns
        ---
        `None`
        """
        # TODO draw cards of opponents and deck
        # TODO figure out what happens if too many cards
        # TODO figure out how to do glow around selected/valid-to-play card

        left_edge = int(self.WINDOW_WIDTH/2
                        - len(self.player.hand)/2 * Client.CARD_OFFSET
                        - Card.IMG_WIDTH/4)

        for (index, card) in enumerate(self.player.hand):
            card.display(self.window, left_edge + index *
                         Client.CARD_OFFSET, Client.CARD_YPOS, 0.5)

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

        match self.state:
            case Client.STATE_START:
                self.button.draw()

                # use the correct cursor
                # selecting button
                if self.button.check_hover():
                    pygame.mouse.set_cursor(
                        pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND))
                    if self.button.just_entered:
                        self.flip_sound.play()
                # default arrow
                else:
                    pygame.mouse.set_cursor(
                        pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW))
                    self.mouse_hovering = False

            case Client.STATE_WAIT:
                if self.announcement != "":
                    self.draw_announcement()

                # default arrow
                pygame.mouse.set_cursor(
                    pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW))

            case Client.STATE_PLAY:
                self.draw_cards()

                # default arrow
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

            match self.state:
                case Client.STATE_START:
                    message = "start"
                case Client.STATE_WAIT:
                    message = "wait"
                case Client.STATE_PLAY:
                    message = "play"
                case Client.STATE_END:
                    message = "end"
            if not self.announcement_sticky:
                self.announcement = ""

            # handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONUP:
                    if self.button.check_hover():
                        self.tap_sound.play()
                        self.button.visible = False
                        message = "ready"
                        self.state = Client.STATE_WAIT

            # handle updates from server
            reply = self.send_request(message)
            match reply.split()[0]:
                case "start":
                    pass
                case "wait":
                    wait_counter = reply.split()[1:]
                    if wait_counter[0] == wait_counter[1]:
                        self.state = Client.STATE_PLAY
                    else:
                        self.announcement = f"Waiting for players to ready..." +\
                            f"{wait_counter[0]}/{wait_counter[1]} ready."
                case "play":
                    self.player = Player(reply[len("play "):])
                    self.player.sort_cards()
            # draw things
            self.draw()
            pygame.display.update()

    class Button:
        """
        `Button` inner class for the UI.
        """

        def __init__(self, window: pygame.Surface, text: str, pos: tuple[int, int],
                     fg: tuple[int, int, int], bg: tuple[int, int, int],
                     font: pygame.freetype.Font) -> None:
            """
            Constructor.

            Parameters
            ---
            `window: pygame.Surface` - window this belongs to (is drawn on).
            `text: str` - button text.
            `pos: tuple[int, int]` - position of the button on the window.
            `fg: tuple[int, int, int]` - RGB color of the text.
            `bg: tuple[int, int, int]` - RGB color of the background.

            Returns
            ---
            `None`
            """
            self.window: pygame.Surface = window
            self.text: str = text
            self.pos: tuple[int, int] = pos
            self.fg: tuple[int, int, int] = fg
            self.bg: tuple[int, int, int] = bg
            self.font: pygame.font.Font = font
            self.visible: bool = True
            self.hovered: bool = False
            self.just_entered: bool = False

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

            text_surface, text_rect = self.font.render(self.text, fg, bg)
            button_rect: pygame.Rect = text_rect.copy()
            button_rect.inflate_ip(Client.BOX_PADDING, Client.BOX_PADDING)
            button_rect.center = self.pos

            if button_rect.collidepoint(pygame.mouse.get_pos()):
                fg = self.bg
                bg = self.fg
            pygame.draw.rect(self.window, bg, button_rect,
                             border_radius=int(button_rect[3]/5))
            if button_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.window, fg, button_rect, width=2,
                                 border_radius=int(button_rect[3]/5))

            text_surface, text_rect = self.font.render(self.text, fg, bg)
            text_rect.center = self.pos
            self.window.blit(text_surface, text_rect)

            self.rect = button_rect

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
            prev = self.hovered
            self.hovered = self.visible and self.rect.collidepoint(
                pygame.mouse.get_pos())
            self.just_entered = not prev and self.hovered
            return self.hovered


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
