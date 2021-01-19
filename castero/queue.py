from castero import constants
from castero.config import Config
from castero.player import Player


class Queue:
    """A FIFO ordered queue of Player instances.

    This class is also the display class' main interface for accessing
    information about the current player.
    """
    MIN_VOLUME = 0
    MAX_VOLUME = 100
    MIN_SPEED = 0.5
    MAX_SPEED = 2.0

    def __init__(self, display) -> None:
        self._players = []
        self._display = display
        self._volume = int(Config["default_volume"])
        self._speed = float(Config["default_playback_speed"])
        self._resume_rewind = int(Config["resume_rewind_distance"])
        self._sanitize_volume()
        self._sanitize_speed()

    def __getitem__(self, index):
        return self._players[index]

    def __iter__(self):
        return self._players.__iter__()

    def clear(self) -> None:
        """Clears the queue.

        It is extremely likely that the caller of this method will also want to
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
            self._display.modified_episodes.append(self.first.episode)
            progress = self.first.episode.progress
            if progress is None or progress == 0:
                self.first.play()
            else:
                self._play_from_progress()
            self.first.set_volume(self.volume)
            self.first.set_rate(self.speed)

    def _play_from_progress(self):
        """Seek forward to progress from start of episode
        """
        progress = self.first.episode.progress
        if progress is not None and progress != 0:
            resume_point = self.first.episode.progress / constants.MILLISECONDS_IN_SECOND

            # Only rewind when state was stopped
            if self.first.state == 0:
                resume_point -= self._resume_rewind

            self.first.play_from(resume_point)

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
            distance = int(
                Config[
                    "seek_distance_forward" if direction == 1 else
                    "seek_distance_backward"
                ]
            )
            self.first.seek(direction, distance)

    def change_rate(self, direction, display=None) -> None:
        """Increase or decrease the playback speed of the first player.

        Args:
            direction: 1 to increase, -1 to decrease
            display: (optional) the display to write status updates to
        """
        assert direction == 1 or direction == -1
        
        # First we change our speed value, then we set the player speed
        # to that amount. This ensures the player speed is always derived
        # from our value.
        self._speed += 0.1 * direction
        self._sanitize_speed()

        if self.first is not None:
            self.first.set_rate(self.speed)
            #Update the display status
            self._display.change_status (
                "Playback speed set to {:0.2f}".format(self.speed))

    def change_volume(self, direction) -> None:
        """Increase or decrease volume of the current player.

        Args:
            direction: 1 to increase, -1 to decrease
        """
        assert direction == 1 or direction == -1

        # First we change our volume value, then we set the player volume
        # to that amount. This ensures the player volume is always derived
        # from our value.
        self._volume += int(Config["volume_adjust_distance"]) * direction
        self._sanitize_volume()

        if self.first is not None:
            self.first.set_volume(self._volume)

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
        if self.first is not None and self.first.duration is not None:
            # sanity check the player's current time
            if self.first.duration > 0:
                if (self.first.time / constants.MILLISECONDS_IN_SECOND) + 1 >= \
                        (self.first.duration / constants.MILLISECONDS_IN_SECOND):
                    self.first.episode.played = True
                    self.first.episode.progress = None
                    self._display.modified_episodes.append(self.first.episode)
                    self.next()
                    self.play()

    def get_episode_progress(self):
        """ Get progress of the current playing episode
        Returns:
            Tuple: episode and its progress if currently playing, else
            None is returned
        """
        if self.first is not None:
            return (self.first.episode, self.first.time)
        return (None, None)

    def _sanitize_volume(self) -> None:
        """Ensure the volume is an acceptable value (0-100 inclusive).
        """
        if self._volume > self.MAX_VOLUME:
            self._volume = self.MAX_VOLUME
        elif self._volume < self.MIN_VOLUME:
            self._volume = self.MIN_VOLUME

    def _sanitize_speed(self) -> None:
        """Ensure the speed is an acceptable value (0.5-2.0 inclusive)
        """
        if (self._speed < self.MIN_SPEED):
            self._speed = self.MIN_SPEED
        elif self._speed > self.MAX_SPEED:
            self._speed = self.MAX_SPEED

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

    @property
    def volume(self) -> int:
        """int: the current playback volume"""
        return self._volume

    @property
    def speed(self) -> float:
        """float: the current playback speed"""
        return self._speed