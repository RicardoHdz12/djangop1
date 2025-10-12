from django.urls import path
from . import views  
from django.contrib import admin

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('admin/', admin.site.urls),

    

]
