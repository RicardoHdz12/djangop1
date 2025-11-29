from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created:
        activation_link = f"http://localhost:8500/activate/{instance.pk}/"

        subject = "Activa tu cuenta"
        message = (
            f"Hola {instance.username},\n\n"
            f"Gracias por registrarte en nuestra plataforma.\n\n"
            f"Para activar tu cuenta, haz clic en el siguiente enlace:\n"
            f"{activation_link}\n\n"
            f"Si tú no creaste esta cuenta, puedes ignorar este correo.\n\n"
            f"Saludos,\n"
            f"Equipo LMS"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=False,
        )
