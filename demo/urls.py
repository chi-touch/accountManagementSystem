from django.urls import path
from . import views

urlpatterns = [
    path("hello", views.say_hello),
    path("welcome/", views.welcome),
]

# python manage.py runserver     // this how to run server
# python manage.py startapp account // adding a new class
