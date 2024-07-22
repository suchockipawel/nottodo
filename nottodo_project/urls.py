from schema_graph.views import Schema
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('nottodo.urls')),
    path('schema/', Schema.as_view()),
]
