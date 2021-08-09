from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from .scoring import Scoreboard


class IncreaseScore(View):
    def post(self, request, sbid, pid, amount):
        sb = Scoreboard(sbid)
        sb[pid] + amount
        return HttpResponse()


class DecreaseScore(View):
    def post(self, request, sbid, pid, amount):
        sb = Scoreboard(sbid)
        sb[pid] - amount
        return HttpResponse()


class Reset(View):
    def post(self, request, sbid):
        sb = Scoreboard(sbid)
        sb.reset()
        return HttpResponse()


class Home(TemplateView):
    template_name = 'score/home.html'

    def get_context_data(self, **kwargs):
        scoreboard = Scoreboard()
        return {
            'js_vars': {
                'ws_url': reverse('websocket', args=(scoreboard.sbid,), urlconf='score.routing'),
            },
            'sb': scoreboard,
            'step': 5,
            **super().get_context_data(**kwargs),
        }
