import smtplib
from email.message import EmailMessage

def send_email(smtp_data, recipient, subject, content):
    try:
        msg = EmailMessage()
        msg["From"] = smtp_data["username"]
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(content)

        with smtplib.SMTP_SSL(smtp_data["host"], smtp_data["port"]) as smtp:
            smtp.login(smtp_data["username"], smtp_data["password"])
            smtp.send_message(msg)

        return True, None
    except Exception as e:
        return False, str(e)
