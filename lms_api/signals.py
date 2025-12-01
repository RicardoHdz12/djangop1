from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from allauth.socialaccount.models import SocialAccount


@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    """
    Envía correo de activación cuando el usuario se registra manualmente.
    """
    if not created:
        return

    if not instance.email:
        return

    # Link de activación
    activation_link = f"http://localhost:8500/activate/{instance.pk}/"

    subject = "Activa tu cuenta"
    message = (
        f"Hola {instance.username},\n\n"
        "Gracias por registrarte en nuestra plataforma.\n\n"
        "Para activar tu cuenta, haz clic en el siguiente enlace:\n"
        f"{activation_link}\n\n"
        "Si tú no creaste esta cuenta, puedes ignorar este correo.\n\n"
        "Saludos,\n"
        "Equipo LMS"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [instance.email],
        fail_silently=False,
    )


