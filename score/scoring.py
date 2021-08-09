from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache

from .hardware import set_display


class Player:
    min_score = 0
    max_score = 100
    start_score = 0

    def __init__(self, scoreboard, pid):
        self.scoreboard = scoreboard
        self.pid = pid

        self.score = self.start_score
        self.cache_key = 'sb%d_p%d' % (scoreboard.sbid, pid)

        cache_score = cache.get(self.cache_key, self.start_score)
        self._set_score(cache_score, initial=True)

    def as_dict(self):
        return {
            'pid': self.pid,
            'score': self.score,
            'str': str(self),
        }

    def reset(self):
        self._set_score(self.start_score)

    def __add__(self, other):
        self._set_score(self.score + int(other))
        return self

    def __sub__(self, other):
        self._set_score(self.score - int(other))
        return self

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.score == other.score
        try:
            return self.score == int(other)
        except TypeError:
            return False

    def __str__(self):
        max_score = 10 ** self.scoreboard.digits - 1
        score = min(self.score, max_score)
        return "%02d" % score

    def _set_score(self, score, initial=False):
        new_score = max(min(score, self.max_score), self.min_score)
        if new_score == self.score:
            return
        self.score = new_score
        if not initial:
            cache.set(self.cache_key, self.score, timeout=None)
            self.scoreboard.broadcast()


class Scoreboard:
    max_scoreboards = 1
    max_players = 2
    max_digits = 2
    player_class = Player

    def __init__(self, sbid=0, players=2, digits=2):
        if (
            sbid + 1 > self.max_scoreboards
            or players > self.max_players
            or digits > self.max_digits
        ):
            raise ValueError
        self.sbid = sbid
        self.digits = digits
        self.players = tuple(
            self.player_class(self, pid)
            for pid in range(players)
        )

    def as_dict(self):
        return {
            'sbid': self.sbid,
            'players': [
                player.as_dict()
                for player in self.players
            ],
        }

    def broadcast(self):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f'sb{self.sbid}', {
            'type': 'update',
            'data': self.as_dict(),
        })
        set_display(''.join(
            str(player)
            for player in self.players
        ))

    def reset(self):
        for player in self.players:
            player.reset()

    def __getitem__(self, item):
        return self.players[item]
