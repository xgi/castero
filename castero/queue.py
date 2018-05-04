from castero.player import Player


class Queue:
    """The Queue class.

    A FIFO ordered queue of Player instances. This class is also the display
    class' main interface for accessing information about the current player.
    """

    def __init__(self, config) -> None:
        """Initializes the object.
        """
        self._players = []
        self._config = config

    def clear(self) -> None:
        """Clears the queue.

        Tt is extremely likely that the caller of this method will also want to
        stop the first player prior to calling this method.
        """
        for p in self._players:
            del p
        self._players = []

    def next(self) -> None:
        """Proceed to the next player in the queue.
        """
        if len(self._players) > 0:
            self._players.pop(0)
            self.play()

    def add(self, player) -> None:
        """Adds a player to the end of the queue.
        """
        assert type(player) == Player

        self._players.append(player)

    def play(self) -> None:
        """Plays the first player in the queue.
        """
        if self.first is not None:
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
            self.first.seek(direction, int(self._config["seek_distance"]))

    def update(self) -> None:
        """Checks the status of the current player.
        """
        if self.first is not None:
            # sanity check the player's current time
            if self.first.duration > 0:
                if (self.first.time / 1000) + 1 >= \
                        (self.first.duration / 1000):
                    self.next()

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
