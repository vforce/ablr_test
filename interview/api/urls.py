from django.urls import path

from . import views

urlpatterns = [
    path("callback", views.singpass_callback, name="callback"),
    # path("results", views.display_result, name="display_result"),
    path("", views.index, name="index"),
]
