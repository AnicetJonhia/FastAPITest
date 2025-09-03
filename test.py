import smtplib

smtp_server = "smtp.office365.com"
port = 587
email = "anicet@futurmap.com"
password = "Jonhia1086*"

try:
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(email, password)
    print("✅ Authentification réussie !")
    server.quit()
except Exception as e:
    print("❌ Erreur :", e)
