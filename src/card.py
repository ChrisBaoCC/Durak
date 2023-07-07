#!usr/bin/env python3
"""
`card` module. Provides the `Card` class.
"""

__author__ = "Chris Bao"
__version__ = 0.9

import pygame


class Card:
    """
    `Card` class. Holds info on a specific card and defines
    display behavior.
    """

    ### Constants ###
    SPADES: int = 0
    HEARTS: int = 1
    CLUBS: int = 2
    DIAMONDS: int = 3

    BACK: int = 52

    VALUE_CONVERT: dict[int, str] = {
        0: 'a',
        1: '2',
        2: '3',
        3: '4',
        4: '5',
        5: '6',
        6: '7',
        7: '8',
        8: '9',
        9: 't',
        10: 'j',
        11: 'q',
        12: 'k',
    }

    SUIT_CONVERT: dict[int, str] = {
        0: 's',
        1: 'h',
        2: 'c',
        3: 'd',
    }

    IMG_WIDTH: int = 179
    IMG_HEIGHT: int = 250

    # Static variables
    images: dict[int, pygame.Surface] = {}

    def load_images() -> None:
        """
        Load all card images into memory.

        Parameters
        ---
        (no parameters)

        Returns
        ---
        `None`
        """
        # card images
        for id in range(0, 52):
            Card.images[id] = pygame.transform.scale_by(pygame.image.load(
                Card.get_path(id)).convert_alpha(), 0.5)
        
        # card back
        Card.images[52] = pygame.transform.scale_by(pygame.image.load(
            "../res/card/back.png").convert_alpha(), 0.5)

    def __init__(self, id: int) -> None:
        """
        Constructor.

        Parameters
        ---
        `id: int` - card ID number, within the range [0, 52) if normal.
        Special id 52 represents the card back.

        Raises
        ---
        `ValueError` - card ID number outside range [0, 52).

        Returns
        ---
        `None`
        """
        if id not in range(0, 53):
            raise ValueError("id must be in range [0, 52) or be 52")

        self.id: int = id
        if id < 52:
            self.suit: int = id // 13
            self.value: int = id % 13
        else:
            self.suit = self.value = -1
        self.image: pygame.Surface = Card.images[id]

    def get_path(id: int) -> str:
        """
        Get the file path for the given card's image.

        Parameters
        ---
        `id: int` - id of the card.

        Returns
        ---
        `str`
        """
        suit = id // 13
        value = id % 13
        return "../res/card/" + Card.VALUE_CONVERT[value] +\
            Card.SUIT_CONVERT[suit] + ".png"

    def touching(self, top_left: tuple[int, int], point: tuple[int, int]) -> bool:
        """
        Determine whether the card is touching the given point when
        drawn at the given position.
        
        Parameters
        ---
        `top_left: tuple[int, int]` - coordinates of top left corner.
        `point: tuple[int, int]` - coordinates to check.
        
        Returns
        ---
        `bool`
        """
        rect = Card.images[self.id].get_rect()
        rect.x, rect.y = top_left
        return rect.collidepoint(*point)


    def display(self, surface: pygame.Surface, x: int, y: int, angle: int=0) -> None:
        """
        Draw this card to the given surface.

        Parameters
        ---
        `surface: pygame.Surface` - screen to draw on.
        `x: int` - x-coordinate of top-left corner.
        `y: int` - y-coordinate of top-left corner.
        `angle: int=0` - rotation.

        Returns
        ---
        `None`
        """
        surface.blit(pygame.transform.rotate(Card.images[self.id], angle), (x, y))
