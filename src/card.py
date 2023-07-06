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

    IMG_WIDTH: tuple[int] = 179
    IMG_HEIGHT: tuple[int] = 250

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
        # TODO: load card back
        for id in range(0, 52):
            Card.images[id] = pygame.transform.scale_by(pygame.image.load(
                Card.get_path(id)).convert_alpha(), 0.5)

    def __init__(self, id: int) -> None:
        """
        Constructor.

        Parameters
        ---
        `id: int` - card ID number, within the range [0, 52).

        Raises
        ---
        `ValueError` - card ID number outside range [0, 52).

        Returns
        ---
        `None`
        """
        if id not in range(0, 52):
            raise ValueError("id must be in range [0, 52)")

        self.id: int = id
        self.suit: int = id // 13
        self.value: int = id % 13
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

    def display(self, surface: pygame.Surface, x: int, y: int, scale: float = 1) -> None:
        """
        Draw this card to the given surface.

        Parameters
        ---
        `x: int` - x-coordinate of top-left corner.
        `y: int` - y-coordinate of top-left corner.
        `scale: float = 1` - scale factor. Must be >= 0.

        Returns
        ---
        `None`

        Raises
        ---
        `ValueError` - when scale factor < 0.
        """
        if scale < 0:
            raise ValueError()

        if scale != 1:
            scaled = pygame.transform.scale_by(Card.images[self.id], scale)
            surface.blit(scaled, (x, y))
        else:
            surface.blit(Card.images[self.id], (x, y))
