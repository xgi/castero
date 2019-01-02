from .. import menu

class EpisodeMenu(menu.Menu):
    def __init__ (self, window, feeds, child = None, active = False, config = None) -> None:
        """Adds flags to episode titles based on metadata before the name list is
        passed to the underlying Menu.  Currently only flags whether an episode
        has been downloaded."""

        feed_ep_array = []
        for fkey in feeds:
            real_feed = feeds[fkey]
            items = []
            for ep in real_feed.episodes:
                flags = []
                if ep.downloaded(config):
                    flags.append("D")

                if flags:
                    items.append("[%s] %s" % ("".join(flags), str(ep)))
                else:
                    items.append(str(ep))
            feed_ep_array.append(items)

        super().__init__(window, feed_ep_array, child, active)
