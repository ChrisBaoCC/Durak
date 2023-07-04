#!usr/bin/env python3
"""
`game` module. Provides the `Player` and `Game` classes.
"""

__author__ = "Chris Bao"
__version__ = 0.9

### Imports ###
from card import Card
from random import shuffle
from collections import deque


class Player:
    """
    `Player` class. Holds all relevant info on a player and their hand
    and defines behavior for playing and receiving cards.
    """

    ### Constructors ###
    def __init__(self, hand_string: str = None) -> None:
        """
        Constructor.

        Parameters
        ---
        hand_string: str = None - (optional) 

        Returns
        ---
        `None`
        """
        self.hand: list[Card] = []
        if hand_string is not None:
            for card_string in hand_string.split(" "):
                if card_string != "" and card_string != "Player:":
                    self.hand.append(Card(int(card_string)))

    def sort_cards(self) -> None:
        """
        Arrange cards in the player's hand.

        Parameters
        ---
        (no parameters)

        Returns
        `None`
        """
        self.hand.sort(key=lambda card: card.id)

    def deal_card(self, card: Card) -> None:
        """
        Receive a card. Called by the `Game` instance.

        Parameters
        ---
        `card: Card` - card to be added to hand.

        Returns
        ---
        `None`
        """
        self.hand.append(card)

    def play_card(self, card: Card) -> None:
        """
        Remove a card. Called by the `Game` instance.

        Parameters
        ---
        `card: Card` - card to be removed from hand.

        Returns
        ---
        `None`
        """
        self.hand.remove(card)

    def __str__(self) -> str:
        """
        Return a string representation of this `Player`.
        (Really just returns what's contained in their hand.)

        Parameters
        ---
        (no parameters)

        Return
        ---
        `str` - space-separated list of card IDs.
        """
        return "Player: " + " ".join([str(card.id) for card in self.hand])


class Game:
    """
    `Game` class. Holds all relevant info about the game in session
    and provides methods for game events.
    """

    ### Constants ###
    MAX_PLAYERS: int = 6

    PHASE_ATTACK: int = 0
    PHASE_DEFEND: int = 1

    CONDITION_ONGOING: int = -1
    CONDITION_DRAW: int = -2

    ### Instance variables ###
    # Game-long variables
    players: list[Player]
    """An array of all players playing, whether active or not"""
    num_players: int
    """Number of players."""
    player_active: list[bool]
    """An array indicating whether the player at the given index is active,
    i.e., has not finished their entire hand."""
    num_active: int
    """Number of active players."""
    deck: deque[Card]
    """A deque of all the cards left to draw."""
    discard: list[Card]
    """A list of all cards that have been discarded."""
    trump_suit: int
    """Tracks the trump suit; uses the suit numbers in `Card`."""

    # Turn-dependent variables
    attacking: int
    """Player whose turn it is to attack."""
    defending: int
    """Player whose turn it is to defend."""
    phase: int
    """Tracks whether someone has committed to a defense
    (`PHASE_DEFEND`) or not (`PHASE_ATTACK`)."""
    pairs: list[list[Card]] = []
    """Tracks pairs of cards that are attacking/defending"""

    def __init__(self, players: list[Player]) -> None:
        """
        Constructor.

        Parameters
        ---
        `players: list[Player]` - players joining the game

        Raises
        ---
        `ValueError` - too many players.

        Returns
        ---
        `None`
        """
        # catch problems
        if len(players) > Game.MAX_PLAYERS:
            raise ValueError(f"too many players (max: {Game.MAX_PLAYERS})")

        # get players
        self.players: list[Player] = players
        self.num_players: int = len(players)
        self.player_active: list[bool] = [True, ] * len(self.players)
        self.num_active: int = len(players)

        # initialize deck
        # the "top" of the deck is the left, the "bottom" is the right
        # dealing the cards will use `popleft()` while displaying
        # the bottom card will involve subscripting - `self.deck[-1]`
        self.deck = [Card(i) for i in range(52)]
        shuffle(self.deck)
        self.deck: deque[Card] = deque(self.deck)
        self.discard: list[Card] = []

        # deal initial hands
        for player in self.players:
            for _ in range(6):
                player.deal_card(self.deck.popleft())
        self.trump_suit: int = self.deck[-1].suit

        # determine who goes first
        self.attacking: int = 0
        lowest_trump = 13  # highest rank is 12, lowest is 0
        for (index, player) in enumerate(self.players):
            for card in player.hand:
                if card.suit == self.trump_suit and\
                        card.value < lowest_trump:
                    lowest_trump = card.value
                    self.attacking = index
        self.defending: int = (self.attacking + 1) % self.num_players

        self.phase: int = Game.PHASE_ATTACK
        # contains the pairs of cards that are being played/covered
        self.pairs: list[list[Card]] = []

    def get_next_available(self, player: int) -> int | None:
        """
        Return the next available player (available meaning has not finished their hand).

        Parameters
        ---
        `player: int` - index of current player

        Returns
        ---
        `int` - index of next available player, or
        `None` - if no other players available.
        """
        index = player
        while True:
            index = (index + 1) % self.num_players

            # no other available players
            if player == index:
                return None

            # first active player found
            if self.player_active[index]:
                return index

    def check_covers(self, card: Card, target: Card) -> bool:
        """
        Test if a card can cover another.

        Parameters
        ---
        `card: Card` - card to be played.
        `target: Card` - card to be covered.

        Returns
        ---
        `bool` - `True` if covers, `False` if not.
        """
        # trump suit beats any other suit
        if card.suit == self.trump_suit and target.suit != self.trump_suit:
            return True
        # else has to be higher and same suit
        return card.suit == target.suit and card.value > target.value

    def can_add_to_attack(self, card: Card) -> bool:
        """
        Test if the card to be played can be added to the attack.
        To be valid, it must share rank with a card already on the board.

        Parameters
        ---
        `card: Card` - card to be added

        Returns
        ---
        `bool` - `True` if can be added, `False` otherwise
        """
        # first check that defender has enough cards to defend everything
        to_be_covered = 0
        for pair in self.pairs:
            if len(pair) < 2:
                to_be_covered += 1
        # defender's hand size must be >= [attacking cards remaining] + 1
        # (since we're adding one)
        if len(self.players[self.defending].hand) <= to_be_covered:
            return False

        for pair in self.pairs:
            for played_card in pair:
                if card.value == played_card.value:
                    return True
        return False

    def can_play_card(self, player: int, card: Card,
                      covering: int = None) -> bool:
        """
        Test if the given card is playable by the given player.

        Parameters
        ---
        `player: int` - index of the player playing the card.
        `card: Card` - card being played.
        `covering: int = None` - index of card being covered in `self.pairs`.

        Returns
        ---
        `bool` - `True` if playable, `False` if not
        """
        # doesn't own the card
        if card not in self.players[player].hand:
            return False

        if self.phase == Game.PHASE_ATTACK:
            # player is the target of the attack
            if player == self.defending:
                # must wait for attack to play anything
                if len(self.pairs) == 0:
                    return False

                # committing to defense
                if covering is not None:
                    return self.check_covers(card, self.pairs[covering][0])
                # turning the attack
                else:
                    # first check that defender has enough cards to defend everything
                    next_available = self.get_next_available(player)
                    if next_available is None:
                        return False
                    to_be_covered = len(self.pairs)
                    # defender's hand size must be >= [attacking cards remaining] + 1
                    # (since we're adding one)
                    if len(self.players[next_available].hand) <= to_be_covered:
                        return False

                    return card.value == self.pairs[0][0].value

            # player is not the target
            else:
                # first attack, anything is possible
                if len(self.pairs) == 0:
                    return True
                # adding to the attack
                return self.can_add_to_attack(card)

        else:  # self.phase == Game.PHASE_DEFEND
            # player is the target of the attack
            if player == self.defending:
                # can't pass on attack anymore
                if covering is None:
                    return False
                # must cover something
                return self.check_covers(card, self.pairs[covering][0])

            # player is not the target, adding to the attack
            else:
                return self.can_add_to_attack(card)

    def play_card(self, player: int, card: Card, covering: int = None):
        """
        Has the given player play the given card.

        Parameters
        ---
        `player: int` - index of the player playing the card.
        `card: Card` - card being played.
        `covering: int = None` - index of card being covered in `self.pairs`.

        Raises
        ---
        `AssertionError` - if card not playable by this player.

        Returns
        ---
        `None`
        """
        assert self.can_play_card(player, card, covering),\
            "card not playable by this player"

        if self.phase == Game.PHASE_ATTACK:
            # player is the target of the attack
            if player == self.defending:
                # committing to defense
                self.phase = Game.PHASE_DEFEND
                if covering is not None:
                    self.pairs[covering].append(card)
                # turning the attack
                else:
                    self.defending = self.get_next_available(player)
                    self.pairs.append([card, ])
            # player is not the target, adding to the attack
            else:
                self.pairs.append([card, ])
        else:  # self.phase == Game.PHASE_DEFEND
            # player is the target of the attack
            if player == self.defending:
                self.pairs[covering].append(card)
            # player is not the target, attacking or adding to the attack
            else:
                self.pairs.append([card, ])

        self.players[player].play_card(card)

    def check_finished(self) -> int:
        """
        Update activity of all players and check whether the game is finished.
        (Active = still has cards left to play.)

        Parameters
        ---
        (no parameters)

        Returns
        ---
        `int` -
            * `Game.CONDITION_ONGOING` if there are multiple active players;
            * `Game.CONDITION_DRAW` if there are no active players (draw);
            * the index of the loser if there is exactly one active player.
        """
        self.player_active = [len(player.hand) > 0 for player in self.players]
        self.num_active = sum(self.player_active)
        if self.num_active > 1:
            return Game.CONDITION_ONGOING
        if self.num_active == 0:
            return Game.CONDITION_DRAW
        for index in range(len(self.players)-1):
            if len(self.players[index].hand) > 0:
                return index
        return self.num_players-1

    def refill_hands(self) -> None:
        """
        Refill each player's hands to 6 cards while there are still cards
        left in the deck. Attacker draws first; defender draws last.

        Parameters
        ---
        (no parameters)

        Returns
        ---
        `None`
        """
        for i in range(self.num_players):
            deal_target = (self.attacking + i) % self.num_players
            # skip the defender for last
            if deal_target == self.defending:
                continue
            # skip people who are done
            if not self.player_active[deal_target]:
                continue
            while len(self.deck) > 0 and len(self.players[deal_target].hand) < 6:
                self.players[deal_target].deal_card(self.deck.popleft())
            if len(self.deck) == 0:
                return

        if not self.player_active[self.defending]:
            return
        while len(self.deck) > 0 and len(self.players[self.defending].hand) < 6:
            self.players[self.defending].deal_card(self.deck.popleft())

    def reset_round(self) -> None:
        """
        Clear off the board, putting cards into the defender's hand or discard
        pile as necessary. Then update game state and deal remaining players new cards.

        Parameters
        ---
        (no parameters)

        Returns
        ---
        `None`
        """
        defense_successful = True
        for pair in self.pairs:
            if len(pair) < 2:
                defense_successful = False
                break

        # clear everything; defender becomes attacker
        if defense_successful:
            for pair in self.pairs:
                for card in pair:
                    self.discard.append(card)
            self.pairs.clear()
            condition = self.check_finished()
            if condition != Game.CONDITION_ONGOING:
                return

            self.refill_hands()

            self.attacking = self.defending
            self.defending = self.get_next_available(self.attacking)
        # defender takes all cards; next person is attacker
        else:
            for pair in self.pairs:
                for card in pair:
                    self.players[self.defending].deal_card(card)
            self.pairs.clear()
            condition = self.check_finished()
            if condition != Game.CONDITION_ONGOING:
                return

            self.refill_hands()

            self.attacking = self.get_next_available(self.defending)
            self.defending = self.get_next_available(self.attacking)
