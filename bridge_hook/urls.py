from django.conf.urls import url, include
from bridge_hook.views import webhook

urlpatterns = [
    url('', webhook),
]
