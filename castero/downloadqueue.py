import threading

from castero.episode import Episode


class DownloadQueue:
    """The DownloadQueue class.

    A FIFO ordered queue for handling episode downloads.
    """

    def __init__(self, display=None) -> None:
        """Initializes the object.
        """
        self._episodes = []
        self._display = display

    def next(self) -> None:
        """Proceed to the next episode in the queue.
        """
        if len(self._episodes) > 0:
            self._episodes.pop(0)
            self.start()

    def add(self, episode) -> None:
        """Adds an episode to the end of the queue.
        """
        assert isinstance(episode, Episode)

        if episode not in self._episodes:
            self._episodes.append(episode)

    def start(self) -> None:
        """Start downloading the first episode in the queue.
        """
        if self.first is not None:
            self.first.download(self, self._display)

    def update(self) -> None:
        """Checks the status of the current download.
        """
        # if nothing is downloading, start downloading the first episode
        found_downloading = False
        for thread in threading.enumerate():
            if thread.getName().startswith("download"):
                found_downloading = True
        if not found_downloading and len(self._episodes) > 0:
            self.start()

    @property
    def first(self) -> Episode:
        """Episode: the first episode in the queue"""
        result = None
        if len(self._episodes) > 0:
            result = self._episodes[0]
        return result

    @property
    def length(self) -> int:
        """int: the length of the queue"""
        return len(self._episodes)
