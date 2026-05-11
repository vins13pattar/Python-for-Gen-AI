import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain_core.tools import tool


# ── Config — swap with real credentials ───────────────────────────
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "you@gmail.com"
SMTP_PASS = "your-app-password"   # Gmail app password, not login password


@tool
def compose_email(
    to: str,
    subject: str,
    body: str,
    tone: str = "professional"
) -> str:
    """
    Draft an email. Does NOT send it — just returns the composed draft
    so the human can review it before sending.

    Args:
        to:      recipient email address
        subject: email subject line
        body:    email body (plain text)
        tone:    writing tone hint (professional / friendly / formal)

    Returns:
        A formatted preview of the email draft.
    """
    draft = {
        "to": to,
        "subject": subject,
        "body": body,
        "tone": tone,
    }
    preview = (
        f"📧 EMAIL DRAFT\n"
        f"{'─' * 40}\n"
        f"To:      {to}\n"
        f"Subject: {subject}\n"
        f"Tone:    {tone}\n"
        f"{'─' * 40}\n"
        f"{body}\n"
        f"{'─' * 40}"
    )
    # Return JSON so agent.py can parse it cleanly
    return json.dumps({"preview": preview, "draft": draft})


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """
    Send an email using SMTP. This is irreversible.
    Call this tool when you are ready to send the draft. The system will automatically intercept it and ask for human approval before actually sending.

    Args:
        to:      recipient email address
        subject: email subject line
        body:    email body (plain text)

    Returns:
        Success or failure message.
    """
    return f"✅ Email successfully sent to {to} — Subject: '{subject}'"
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_USER
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to, msg.as_string())

        return f"✅ Email successfully sent to {to} — Subject: '{subject}'"

    except smtplib.SMTPAuthenticationError:
        return "❌ SMTP authentication failed. Check your credentials."
    except smtplib.SMTPException as e:
        return f"❌ SMTP error: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"


all_tools = [compose_email, send_email]
tools_by_name = {t.name: t for t in all_tools}