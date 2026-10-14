import os
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple, Optional

logger = logging.getLogger("SafeBiteEmailService")

def get_smtp_config():
    host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    try:
        port = int(os.getenv("SMTP_PORT", "587").strip())
    except Exception:
        port = 587
    user = os.getenv("SMTP_USERNAME", "nemisharma9257@gmail.com").strip()
    # Strip spaces in case user passes Google 16-char App Password formatted as 'xxxx xxxx xxxx xxxx'
    pw = os.getenv("SMTP_PASSWORD", "rwjcyucbkauigbzu").replace(" ", "").strip()
    sender = os.getenv("EMAIL_FROM", f"SafeBite <{user}>" if user else "no-reply@safebite.app").strip()
    try:
        expire_min = int(os.getenv("VERIFICATION_CODE_EXPIRE_MINUTES", "10"))
    except Exception:
        expire_min = 10
    try:
        cooldown_sec = int(os.getenv("VERIFICATION_RESEND_COOLDOWN_SECONDS", "30"))
    except Exception:
        cooldown_sec = 30
    return host, port, user, pw, sender, expire_min, cooldown_sec

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "nemisharma9257@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "rwjcyucbkauigbzu").replace(" ", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", f"SafeBite <{SMTP_USERNAME}>")
VERIFICATION_CODE_EXPIRE_MINUTES = int(os.getenv("VERIFICATION_CODE_EXPIRE_MINUTES", "10"))
VERIFICATION_RESEND_COOLDOWN_SECONDS = int(os.getenv("VERIFICATION_RESEND_COOLDOWN_SECONDS", "30"))

DUMMY_DOMAINS = (
    "example.com", "example.org", "example.net",
    "safebite.io", "safebite.local", "safebite.internal",
    "test.com", "test.io", "localhost"
)

def is_smtp_configured() -> bool:
    """Returns True if SMTP credentials are provided in the environment."""
    host, _, user, pw, _, _, _ = get_smtp_config()
    return bool(host and user and pw)

def send_verification_email(
    to_email: str,
    code: Optional[str] = None,
    verification_code: Optional[str] = None,
    username: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Sends a professional verification email via TLS-secured SMTP.
    Returns (success: bool, error_message: Optional[str]).
    Never logs the raw verification code or sensitive credentials in production.
    """
    final_code = code or verification_code or ""
    greeting_name = f" {username}" if username else ""

    clean_target = to_email.strip().lower()
    domain = clean_target.split("@")[-1] if "@" in clean_target else ""
    is_test_env = os.getenv("TESTING", "").lower() in ("1", "true", "yes")

    # Guard: Do not attempt outbound SMTP dispatch for dummy test domains
    if domain in DUMMY_DOMAINS or is_test_env:
        logger.info(
            f"Test/dummy email recipient detected ({clean_target}). Simulating email dispatch to prevent bounce-back notifications."
        )
        return True, None

    if not is_smtp_configured():
        logger.warning(
            "SMTP credentials not configured (SMTP_USERNAME/SMTP_PASSWORD unset). "
            f"Simulating email dispatch for recipient {clean_target}."
        )
        return True, None

    try:
        subject = "Verify Your SafeBite Account"

        plain_text = f"""Hello{greeting_name},

Thank you for registering with SafeBite – AI Food Health Analyzer.

Your email verification code is:
{final_code}

This code expires in {VERIFICATION_CODE_EXPIRE_MINUTES} minutes. If you did not request this code, you can ignore this email.

Regards,
SafeBite Team
"""

        html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #0F172A;
      color: #F8FAFC;
      margin: 0;
      padding: 24px;
    }}
    .container {{
      max-width: 520px;
      margin: 0 auto;
      background: #1E293B;
      border-radius: 16px;
      border: 1px solid #334155;
      padding: 32px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }}
    .logo {{
      color: #10B981;
      font-size: 24px;
      font-weight: 800;
      letter-spacing: 0.5px;
      margin-bottom: 20px;
    }}
    .title {{
      font-size: 20px;
      font-weight: 700;
      color: #FFFFFF;
      margin-bottom: 12px;
    }}
    .desc {{
      font-size: 14px;
      color: #94A3B8;
      line-height: 1.6;
      margin-bottom: 24px;
    }}
    .code-box {{
      background: #0F172A;
      border: 2px dashed #10B981;
      border-radius: 12px;
      padding: 18px;
      text-align: center;
      margin: 24px 0;
    }}
    .otp {{
      font-size: 36px;
      font-weight: 800;
      letter-spacing: 10px;
      color: #10B981;
      font-family: monospace;
    }}
    .footer {{
      font-size: 12px;
      color: #64748B;
      margin-top: 24px;
      text-align: center;
      border-top: 1px solid #334155;
      padding-top: 16px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">🌿 SafeBite</div>
    <div class="title">Verify Your SafeBite Account</div>
    <div class="desc">
      Hello{greeting_name},<br><br>
      Thank you for registering with <strong>SafeBite – AI Food Health Analyzer</strong>.<br>
      Please enter the following 6-digit verification code to activate your account:
    </div>
    <div class="code-box">
      <div class="otp">{final_code}</div>
    </div>
    <div class="desc">
      This code will expire in <strong>{VERIFICATION_CODE_EXPIRE_MINUTES} minutes</strong>. If you did not request this verification code, you can safely ignore this email.
    </div>
    <div class="footer">
      Regards,<br>
      <strong>SafeBite Health & Nutrition Team</strong>
    </div>
  </div>
</body>
</html>
"""

        host, port, user, pw, sender, expire_min, _ = get_smtp_config()

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = to_email

        message.attach(MIMEText(plain_text, "plain", "utf-8"))
        message.attach(MIMEText(html_content, "html", "utf-8"))

        context = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(user, pw)
            server.sendmail(sender, [to_email], message.as_string())

        logger.info(f"Verification email successfully sent to recipient: {to_email}")
        return True, None

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False, str(e)
