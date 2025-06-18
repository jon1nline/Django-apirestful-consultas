from django.urls import path
from .views import RegistroUsuario, LoginUsuario, UserView


urlpatterns = [
    path('register/', RegistroUsuario.as_view()),
    path('login/', LoginUsuario.as_view()),
    path('user/' , UserView.as_view())
]