from castero.config import Config
from castero.player import Player


class Queue:
    """The Queue class.

    A FIFO ordered queue of Player instances. This class is also the display
    class' main interface for accessing information about the current player.
    """

    def __init__(self, display) -> None:
        """Initializes the object.
        """
        self._players = []
        self._display = display

    def __getitem__(self, index):
        return self._players[index]

    def __iter__(self):
        return self._players.__iter__()

    def clear(self) -> None:
        """Clears the queue.

        Tt is extremely likely that the caller of this method will also want to
        stop the first player prior to calling this method.
        """
        for p in self._players:
            del p
        self._players = []

    def jump(self, player) -> None:
        """Jump to the given player.

        Players skipped are removed from the queue. If the given player is not
        actually in the queue, this method safely does nothing.

        Args:
            player: the Player to jump to
        """
        if player in self._players:
            index = self._players.index(player)
            if index > 0:
                self.stop()
                self._players = self._players[index:]

    def next(self) -> None:
        """Proceed to the next player in the queue.
        """
        if len(self._players) > 0:
            self._players.pop(0)

    def add(self, player) -> None:
        """Adds a player to the end of the queue.
        """
        assert isinstance(player, Player)

        self._players.append(player)

    def play(self) -> None:
        """Plays the first player in the queue.
        """
        if self.first is not None:
            self.first.episode.played = True
            self._display.modified_episodes.append(self.first.episode)
            self.first.play()

    def pause(self) -> None:
        """Pauses the first player in the queue.
        """
        if self.first is not None:
            self.first.pause()

    def stop(self) -> None:
        """Stops the first player in the queue."""
        if self.first is not None:
            self.first.stop()

    def toggle(self) -> None:
        """Plays or pauses the first player.
        """
        if self.first is not None:
            if self.first.state == 1:  # playing
                self.pause()
            else:  # paused or stopped
                self.play()

    def seek(self, direction) -> None:
        """Seeks the first player in the specified direction.

        Args:
            direction: 1 to move forward, -1 to move backward
        """
        assert direction == 1 or direction == -1

        if self.first is not None:
            distance = int(Config["seek_distance_forward" if direction == 1 else "seek_distance_backward"])
            self.first.seek(direction, distance)

    def remove(self, player) -> int:
        """Remove a player from the queue, if it is currently in it.

        Args:
            player: the Player to remove

        Returns:
            int: the index of the player in the queue, or -1
        """
        result = -1
        if player in self._players:
            result = self._players.index(player)
            self._players.remove(player)
        return result

    def update(self) -> None:
        """Checks the status of the current player.
        """
        if self.first is not None:
            # sanity check the player's current time
            if self.first.duration > 0:
                if (self.first.time / 1000) + 1 >= \
                        (self.first.duration / 1000):
                    self.next()
                    self.play()

    @property
    def first(self) -> Player:
        """Player: the first player in the queue"""
        result = None
        if len(self._players) > 0:
            result = self._players[0]
        return result

    @property
    def length(self) -> int:
        """int: the length of the queue"""
        return len(self._players)
