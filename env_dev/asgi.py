#import os
#from django.core.asgi import get_asgi_application
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'env_dev.settings')
#application = get_asgi_application()
import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'env_dev.settings')

from score.routing import urlpatterns

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter(urlpatterns),
})
