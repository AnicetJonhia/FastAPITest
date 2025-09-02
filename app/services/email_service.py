
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema
from app.core.config import settings

def send_welcome_email(email: str, full_name: str):
    print(f"[Email] Welcome email sent to {email} (name: {full_name})")



# async def send_reset_password_email(email: str, token: str, background_tasks: BackgroundTasks):
#     reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
#
#     message = MessageSchema(
#         subject="Réinitialisation de votre mot de passe",
#         recipients=[email],
#         template_body={"reset_link": reset_link, "expiry": settings.FORGET_PASSWORD_LINK_EXPIRE_MINUTES},
#         subtype="html"
#     )
#
#     fm = FastMail(settings.mail_conf)  # mail_conf = configuration FastMail (SMTP)
#     background_tasks.add_task(fm.send_message, message, template_name="password_reset.html")


async def send_reset_password_email(email: str, token: str, background_tasks: BackgroundTasks):
    reset_link = f"http://localhost:8000/reset-password?token={token}"
    print(f"[TEST] Reset link for {email}: {reset_link}")
