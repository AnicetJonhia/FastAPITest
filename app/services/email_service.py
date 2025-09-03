
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema
from app.core.config import settings
from typing import Dict


def send_welcome_email(email: str, full_name: str):
    # placeholder simple
    print(f"[Email] Welcome email sent to {email} (name: {full_name})")


async def send_reset_password_email(email: str, token: str, background_tasks: BackgroundTasks):
    """
    Envoie un email de reset en utilisant un template HTML (Jinja2) si SMTP configuré.
    Si SMTP non configuré (dev), on affiche le lien dans la console pour tests rapides.
    """
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    template_context: Dict[str, str] = {
        "reset_link": reset_link,
        "expiry_minutes": str(settings.FORGET_PASSWORD_LINK_EXPIRE_MINUTES),
        "company_name": "HelloFmap"
    }

    # DEV fallback: si pas de credentials SMTP, print le lien et retourne
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"[DEBUG EMAIL] Reset link for {email}: {reset_link}")
        return

    # Si on a des creds, envoie via fastapi-mail et template Jinja2
    message = MessageSchema(
        subject="Réinitialisation de votre mot de passe",
        recipients=[email],
        template_body=template_context
    )

    fm = FastMail(settings.mail_conf)
    # send_message est async — on l'ajoute en background (starlette/fastapi gère async)
    background_tasks.add_task(fm.send_message, message, template_name="password_reset.html")

