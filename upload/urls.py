from django.urls import path , re_path

from . import views

app_name='upload'
urlpatterns = [
    path('file', views.uploadfile, name='file'),
]