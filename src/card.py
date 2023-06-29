#!usr/bin/env python3
"""
`card` module. Provides the `Card` class.
"""

__author__ = "Chris Bao"
__version__ = 0.9


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
        self.rank: int = id % 13

        # TODO: set image and display
        # self.image = ...

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
