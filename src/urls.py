from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import CreateAudio, ListAudio

app_name = 'src'

urlpatterns = [
    path('', CreateAudio.as_view(), name='create-view'),
    path('list', ListAudio.as_view(), name='list-view')
    # path('create-audio/', CreateAudioFromPdf.as_view(), name='create-audio'),
    # path('download-file/<int:pk>/', DownloadFile.as_view(), name='download-file'),
    # path('list', ListAudio.as_view(), name='list-view'),
    # path('audio-list/', ListAudioFiles.as_view(), name='audio-list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
