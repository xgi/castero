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
        if len(self._players) > 0:
            p = self._players.pop(0)
            del p
            self.play()

    def add(self, player) -> None:
        assert type(player) == Player

        self._players.append(player)

    def play(self) -> None:
        if self.first is not None:
            self.first.play()

    def pause(self) -> None:
        if self.first is not None:
            self.first.pause()

    def stop(self) -> None:
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
        assert direction == 1 or direction == -1

        if self.first is not None:
            self.first.seek(direction, int(self._config["seek_distance"]))

    def update(self) -> None:
        """Checks the status of the current player.
        """
        #self.next()
        if self.first is not None:
            # sanity check the player's current time
            if self.first.duration > 0:
                if self.first.time >= self.first.duration:
                    self.next()

    @property
    def first(self) -> Player:
        result = None
        if len(self._players) > 0:
            result = self._players[0]
        return result

    @property
    def length(self) -> int:
        return len(self._players)
