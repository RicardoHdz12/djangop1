from django.contrib import admin
from django.urls import path, include
from lms_api import views as my_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(title="LMS API", default_version="v1"),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', my_views.welcome, name='welcome'),
    path('home/', my_views.home, name='home'),
    path('login/', my_views.iniciar_sesion, name="login"),
    path('logout/', my_views.cerrar_sesion, name="logout"),
    path('registro/', my_views.registro_view, name="registro"),
    path('perfil/', my_views.perfil_view, name="perfil"),
    path('ajax/courses/', my_views.list_courses_ajax, name='ajax_list_courses'),
    path('api/', include("lms_api.urls")),
    path('accounts/', include('allauth.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
