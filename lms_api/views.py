from rest_framework import viewsets, permissions 
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings

from .models import Profile, Course, Lesson, Enrollment, Comment
from .serializers import (
    UserSerializer, ProfileSerializer, CourseSerializer,
    LessonSerializer, EnrollmentSerializer, CommentSerializer
)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegistroForm


def google_enabled():
    """
    Verifica si el proveedor de Google está configurado en el sistema.
    """
    try:
        from allauth.socialaccount.models import SocialApp
        return SocialApp.objects.filter(provider='google').exists()
    except:
        return False


def iniciar_sesion(request):
    """
    Vista para iniciar sesión con usuario y contraseña.
    Si las credenciales son correctas, se redirige al home.
    También muestra el botón para iniciar con Google si está configurado
    """
    google_provider_enabled = google_enabled()

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Credenciales incorrectas")

    return render(
        request,
        "usuarios/login.html", 
        {"google_provider_enabled": google_provider_enabled},
    )


def registro_view(request):
    """
    Vista que muestra y procesa el formulario de registro.
    Crea un usuario nuevo y lo deja inactivo hasta que active su cuenta por correo.
    """
    google_provider_enabled = google_enabled()

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_active = False 
            user.save()

            messages.success(request, "Revisa tu correo para activar tu cuenta.")
            return redirect("login")

        else:
            messages.error(request, "Revisa los datos ingresados.")
    else:
        form = RegistroForm()

    return render(request, "usuarios/registro.html", {
        "form": form,
        "google_provider_enabled": google_provider_enabled
    })


@login_required
def perfil_view(request):
    """
    Muestra el perfil del usuario autenticado.
    """
    return render(request, "usuarios/perfil.html")   


def cerrar_sesion(request):
    """
    Cierra la sesión del usuario y lo redirige al login.
    """
    logout(request)
    return redirect("login")


def welcome(request):
    """
    Página de bienvenida que se muestra antes de iniciar sesión.
    """
    return render(request, "welcome.html")


@login_required
def home(request):
    """
    Página principal que ven los usuarios autenticados.
    Aquí se cargan dinámicamente los cursos mediante AJAX.
    """
    return render(request, "home.html")


def list_courses_ajax(request):
    """
    Retorna todos los cursos en formato JSON.
    Esta ruta es consumida por AJAX en el home.
    """
    courses = Course.objects.all().values(
        "id", "title", "description", "level", "language"
    )
    return JsonResponse(list(courses), safe=False)


@login_required
def my_courses(request):
    """
    Muestra todos los cursos en los que el usuario está inscrito,
    junto con su progreso en cada uno.
    """
    enrollments = Enrollment.objects.filter(user=request.user).select_related("course")
    return render(request, "courses/my_courses.html", {"enrollments": enrollments})


@login_required
def course_detail(request, course_id):
    """
    Vista con toda la información detallada del curso seleccionado.
    También muestra si el usuario está inscrito o no.
    """
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()
    enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()

    context = {
        "course": course,
        "lessons": lessons,
        "enrolled": enrolled,
    }
    return render(request, "courses/detail.html", context)


import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@csrf_exempt
@login_required
@require_POST
def enroll_course_ajax(request):
    """
    Endpoint AJAX para inscribirse en un curso.
    """
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return JsonResponse({"error": "Solicitud inválida"}, status=400)

    try:
        data = json.loads(request.body)
        course_id = data.get("course_id")
        course = Course.objects.get(id=course_id)

        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={"status": "active"}
        )

        if not created:
            return JsonResponse({"error": "Ya estás inscrito en este curso"}, status=400)

        return JsonResponse(
            {"status": "ok", "course_title": course.title},
            status=201
        )

    except Course.DoesNotExist:
        return JsonResponse({"error": "Curso no encontrado"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def activate_account(request, user_id):
    """
    Activa la cuenta del usuario después de hacer clic en el enlace enviado por correo.
    También envía un correo de bienvenida al activar la cuenta.
    """
    try:
        user = User.objects.get(id=user_id)

        if not user.is_active:
            user.is_active = True
            user.save()

            # Enviar correo de bienvenida
            if user.email:
                subject = "¡Bienvenido a la plataforma!"
                message = (
                    f"Hola {user.username},\n\n"
                    "Tu cuenta ha sido activada exitosamente.\n\n"
                    "Ya puedes iniciar sesión y comenzar a explorar nuestros cursos.\n"
                    "Estamos felices de que formes parte de esta comunidad.\n\n"
                    "Saludos,\n"
                    "Equipo LMS"
                )

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

        messages.success(request, "Tu cuenta ha sido activada. Ya puedes iniciar sesión.")
        return redirect("login")

    except User.DoesNotExist:
        messages.error(request, "El enlace de activación no es válido.")
        return redirect("welcome")


# ---------------------------
#  VIEWSETS (APIs REST)
# ---------------------------

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API que permite ver usuarios (solo admin).
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API CRUD para perfiles de usuario.
    El perfil pertenece al usuario autenticado.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CourseViewSet(viewsets.ModelViewSet):
    """
    API CRUD para cursos.
    Permite buscar, filtrar y crear cursos.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['level', 'language']
    search_fields = ['title', 'description']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    """
    API CRUD para lecciones de cada curso.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['course']
    search_fields = ['title', 'content']


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    API CRUD para inscripciones.
    Guarda al usuario autenticado como dueño de la inscripción.
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    API CRUD para comentarios de cursos.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
