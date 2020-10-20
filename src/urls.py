from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import CreateAudio, ListAudio,DownloadFile

app_name = 'src'

urlpatterns = [
    path('', CreateAudio.as_view(), name='create-view'),
    path('download-file/<int:pk>/', DownloadFile.as_view(), name='download-file'),
    path('list', ListAudio.as_view(), name='list-view')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
