from django.urls import path
from . import views
from .views import AudioFileUpload
#URLConf
urlpatterns = [
    path('demo/', views.demo),
    path('upload/', AudioFileUpload.as_view(), name='file-upload')
]