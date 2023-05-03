from django.urls import path , re_path

from . import views

app_name='planning'
urlpatterns = [
    path('create', views.create, name='create'),
    path('show', views.show_plan, name='show'),
    path('congres', views.addcongres, name='congres'),
    path("pajax/<int:pk>/<slug:date>", views.ajax_load_planning, name="planning-ajax"),
    path("sajax/<int:pk>/", views.ajax_add_session, name="session-ajax"),
    path("pajax/<int:pk>/", views.ajax_add_pres, name="pres-ajax"),
    path("dajax/<int:pk>/", views.ajax_del_pres, name="pres-del-ajax"),
    #ajout d'une salle
    path("salle-ajax/", views.addOneRoom, name="salle-ajax"),
    path("load-ajax/", views.ajax_load_rooms, name="load-ajax"),
    # modification d'une salle
    path("salle-modif-ajax/", views.updateText, name="salle-modif-ajax"),
    path("salle-del-ajax/", views.deleteRoom, name="salle-del-ajax"),
]