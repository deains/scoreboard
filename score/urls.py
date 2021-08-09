from django.urls import path

from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('incr/<int:sbid>/<int:pid>/<int:amount>', views.IncreaseScore.as_view(), name='increase'),
    path('decr/<int:sbid>/<int:pid>/<int:amount>', views.DecreaseScore.as_view(), name='decrease'),
    path('reset/<int:sbid>', views.Reset.as_view(), name='reset'),
]
