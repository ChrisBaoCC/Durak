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
            Card.images[id] = pygame.image.load(
                Card.get_path(id)).convert_alpha()

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

    # TODO: implement
    def display(self) -> None:
        """
        Display this card to the screen.

        Parameters
        ---
        (no parameters)

        Returns
        ---
        `None`
        """
        raise NotImplementedError
