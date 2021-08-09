import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .scoring import Scoreboard


class Consumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = {}

    def get_scoreboard(self):
        return Scoreboard(self.sbid)

    def connect(self):
        self.sbid = self.scope['url_route']['kwargs']['sbid']
        self.group = 'sb%d' % self.sbid
        async_to_sync(self.channel_layer.group_add)(self.group, self.channel_name)
        self.accept()

        scoreboard = self.get_scoreboard()
        self.update({
            'data': scoreboard.as_dict()
        })

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)

    def update(self, event):
        self.send(text_data=json.dumps(event['data']))
