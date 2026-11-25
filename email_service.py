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
        port = int(os.getenv("SMTP_PORT", "465").strip())
    except Exception:
        port = 465
    user = os.getenv("SMTP_USERNAME", "safebitefoodanalyzer@gmail.com").strip()
    # Strip spaces in case user passes Google 16-char App Password formatted as 'xxxx xxxx xxxx xxxx'
    pw = os.getenv("SMTP_PASSWORD", "ftsaumbhavgzzcaq").replace(" ", "").strip()
    sender = os.getenv("EMAIL_FROM", f"SafeBite <{user}>").strip()
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
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "safebitefoodanalyzer@gmail.com").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "ftsaumbhavgzzcaq").replace(" ", "").strip()
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

def _dispatch_email(
    to_email: str,
    subject: str,
    plain_text: str,
    html_content: str,
    log_tag: str = "Email"
) -> Tuple[bool, Optional[str]]:
    """
    Unified multi-tier email dispatcher:
    1. Primary: Google Apps Script Webhook (Port 443 HTTPS, bypasses ISP port 587 blocks)
    2. Secondary: Brevo REST API (Port 443 HTTPS)
    3. Tertiary: Standard TLS SMTP (Port 587 / 465) via Gmail
    4. Fallback: Safe mock simulation in test environments and dummy domains
    """
    clean_target = to_email.strip().lower()
    domain = clean_target.split("@")[-1] if "@" in clean_target else ""
    is_test_env = os.getenv("TESTING", "").lower() in ("1", "true", "yes")

    # Guard: Do not attempt outbound SMTP dispatch for dummy test domains
    if domain in DUMMY_DOMAINS or is_test_env:
        logger.info(
            f"Test/dummy email recipient detected ({clean_target}). Simulating {log_tag} dispatch to prevent bounce-back notifications."
        )
        return True, None

    try:
        # 1. Primary: Direct Authenticated SMTP (Port 465 SSL, then Port 587 STARTTLS)
        # Using official SafeBite Gmail credentials - fast, direct, and avoids Webhook silent drops
        host, _, user, pw, sender, _, _ = get_smtp_config()
        if host and user and pw:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = sender
            message["To"] = clean_target
            message.attach(MIMEText(plain_text, "plain", "utf-8"))
            message.attach(MIMEText(html_content, "html", "utf-8"))

            # Try Port 465 (SSL) first - fastest & most reliable on cloud instances
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(host, 465, context=context, timeout=12) as server:
                    server.login(user, pw)
                    server.sendmail(sender, [clean_target], message.as_string())
                logger.info(f"{log_tag} successfully sent via SMTPS (Port 465) to: {clean_target}")
                return True, None
            except Exception as ssl_err:
                logger.warning(f"SMTPS (Port 465) failed: {ssl_err}, attempting STARTTLS (Port 587)...")

            # Try Port 587 (STARTTLS)
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP(host, 587, timeout=12) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(user, pw)
                    server.sendmail(sender, [clean_target], message.as_string())
                logger.info(f"{log_tag} successfully sent via SMTP STARTTLS (Port 587) to: {clean_target}")
                return True, None
            except Exception as tls_err:
                logger.warning(f"SMTP STARTTLS (Port 587) failed: {tls_err}, trying Brevo/Webhook fallback...")

        # 2. Alternative HTTPS API: Brevo REST API (HTTPS Port 443)
        brevo_key = os.getenv("BREVO_API_KEY", "").strip()
        if brevo_key:
            try:
                import requests
                sender_email = os.getenv("EMAIL_FROM_ADDRESS", user if user else "no-reply@safebite.app").strip()
                brevo_payload = {
                    "sender": {"name": "SafeBite", "email": sender_email},
                    "to": [{"email": clean_target}],
                    "subject": subject,
                    "htmlContent": html_content
                }
                resp = requests.post(
                    "https://api.brevo.com/v3/smtp/email",
                    headers={"api-key": brevo_key, "Content-Type": "application/json"},
                    json=brevo_payload,
                    timeout=12
                )
                if resp.status_code in (200, 201):
                    logger.info(f"{log_tag} dispatched via Brevo HTTPS API to: {clean_target}")
                    return True, None
                else:
                    logger.warning(f"Brevo API returned {resp.status_code}: {resp.text}")
            except Exception as be:
                logger.warning(f"Brevo API failed: {be}")

        # 3. Tertiary Fallback: Google Apps Script Webhook
        raw_env_webhook = (os.getenv("GMAIL_WEBHOOK_URL") or "").strip()
        if raw_env_webhook.startswith("https://") and len(raw_env_webhook) > 25:
            payload = {
                "email": clean_target,
                "subject": subject,
                "text": plain_text,
                "html": html_content
            }
            try:
                import requests
                resp = requests.post(raw_env_webhook, json=payload, timeout=15, allow_redirects=True)
                if resp.status_code in (200, 302):
                    logger.info(f"{log_tag} dispatched via Webhook to: {clean_target}")
                    return True, None
            except Exception as we:
                logger.warning(f"Webhook dispatch failed: {we}")

        if is_test_env:
            logger.info(f"Test environment active. Simulating {log_tag} dispatch for {clean_target}")
            return True, None

        logger.warning(f"All email dispatch methods failed for {log_tag} to {clean_target}")
        return False, "Failed to send email. Please try again later."

    except Exception as e:
        logger.error(f"Failed to send {log_tag} to {clean_target}: {e}")
        return False, str(e)


def send_verification_email(
    to_email: str,
    code: Optional[str] = None,
    verification_code: Optional[str] = None,
    username: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Sends a professional verification email via TLS-secured SMTP / Webhook / Brevo.
    Returns (success: bool, error_message: Optional[str]).
    Never logs the raw verification code or sensitive credentials in production.
    """
    final_code = code or verification_code or ""
    greeting_name = f" {username}" if username else ""
    clean_target = to_email.strip().lower()

    subject = f"Your SafeBite Verification Code is {final_code}"

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
    <div class="logo"><span style="color:#10B981;font-weight:900;">Safe</span><span style="color:#F8FAFC;font-weight:700;">Bite</span> <span style="font-size:11px;font-weight:600;color:#10B981;border:1px solid #10B981;border-radius:12px;padding:2px 8px;margin-left:6px;vertical-align:middle;text-transform:uppercase;letter-spacing:1px;">Health AI</span></div>
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

    return _dispatch_email(
        to_email=clean_target,
        subject=subject,
        plain_text=plain_text,
        html_content=html_content,
        log_tag="Verification Email"
    )


def get_welcome_email_html(username: Optional[str] = None) -> str:
    """
    Generates a high-quality, responsive HTML Welcome Page email for new SafeBite users.
    """
    display_name = username.strip() if username and username.strip() else "Health Explorer"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Welcome to SafeBite</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #0F172A;
      color: #F8FAFC;
      margin: 0;
      padding: 20px 12px;
      -webkit-font-smoothing: antialiased;
    }}
    .email-wrapper {{
      max-width: 600px;
      margin: 0 auto;
      background: #1E293B;
      border-radius: 20px;
      border: 1px solid #334155;
      overflow: hidden;
      box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }}
    .header-banner {{
      background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #064E3B 100%);
      padding: 36px 32px 28px;
      border-bottom: 1px solid #334155;
      text-align: center;
    }}
    .logo {{
      font-size: 28px;
      font-weight: 900;
      letter-spacing: 0.5px;
      color: #10B981;
      display: inline-block;
      margin-bottom: 8px;
    }}
    .badge {{
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      color: #10B981;
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid #10B981;
      border-radius: 12px;
      padding: 3px 10px;
      margin-left: 8px;
      vertical-align: middle;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    .hero-title {{
      font-size: 24px;
      font-weight: 800;
      color: #FFFFFF;
      margin: 16px 0 8px;
      line-height: 1.3;
    }}
    .hero-subtitle {{
      font-size: 15px;
      color: #94A3B8;
      line-height: 1.5;
      margin: 0;
    }}
    .content-body {{
      padding: 32px;
    }}
    .greeting {{
      font-size: 16px;
      line-height: 1.6;
      color: #CBD5E1;
      margin-bottom: 24px;
    }}
    .section-title {{
      font-size: 18px;
      font-weight: 700;
      color: #F8FAFC;
      margin: 28px 0 16px;
      display: flex;
      align-items: center;
    }}
    .feature-card {{
      background: #0F172A;
      border: 1px solid #334155;
      border-left: 4px solid #10B981;
      border-radius: 12px;
      padding: 16px 18px;
      margin-bottom: 14px;
    }}
    .feature-title {{
      font-size: 15px;
      font-weight: 700;
      color: #10B981;
      margin-bottom: 4px;
    }}
    .feature-desc {{
      font-size: 13.5px;
      color: #94A3B8;
      line-height: 1.5;
      margin: 0;
    }}
    .steps-container {{
      background: #0F172A;
      border: 1px solid #334155;
      border-radius: 14px;
      padding: 20px;
      margin: 20px 0;
    }}
    .step-item {{
      display: flex;
      margin-bottom: 14px;
    }}
    .step-item:last-child {{
      margin-bottom: 0;
    }}
    .step-number {{
      background: #10B981;
      color: #0F172A;
      font-weight: 800;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      text-align: center;
      line-height: 24px;
      font-size: 13px;
      margin-right: 12px;
      flex-shrink: 0;
    }}
    .step-text {{
      font-size: 13.5px;
      color: #CBD5E1;
      line-height: 1.5;
    }}
    .cta-container {{
      text-align: center;
      margin: 32px 0 20px;
    }}
    .cta-button {{
      display: inline-block;
      background: linear-gradient(135deg, #10B981 0%, #059669 100%);
      color: #FFFFFF !important;
      text-decoration: none;
      padding: 14px 32px;
      border-radius: 12px;
      font-weight: 700;
      font-size: 15px;
      letter-spacing: 0.5px;
      box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35);
    }}
    .pro-tip {{
      background: rgba(16, 185, 129, 0.08);
      border: 1px dashed #10B981;
      border-radius: 10px;
      padding: 14px;
      font-size: 13px;
      color: #A7F3D0;
      line-height: 1.5;
      margin: 20px 0;
    }}
    .footer {{
      background: #0F172A;
      border-top: 1px solid #334155;
      padding: 24px 32px;
      text-align: center;
      font-size: 12px;
      color: #64748B;
      line-height: 1.6;
    }}
  </style>
</head>
<body>
  <div class="email-wrapper">
    <!-- Header Banner -->
    <div class="header-banner">
      <div class="logo">Safe<span style="color: #F8FAFC;">Bite</span> <span class="badge">Health AI</span></div>
      <div class="hero-title">Welcome to SafeBite, {display_name}! 🥗</div>
      <p class="hero-subtitle">Your AI-Powered Food Health Analyzer & Smart Nutrition Guide</p>
    </div>

    <!-- Body Content -->
    <div class="content-body">
      <div class="greeting">
        Hello <strong>{display_name}</strong>,<br><br>
        Congratulations on taking a powerful step toward cleaner eating and better health! With <strong>SafeBite</strong>, you no longer have to guess what is hidden in packaged foods. Our intelligent multi-model vision and nutrition engine is here to empower you every time you shop or eat.
      </div>

      <!-- Key Capabilities -->
      <div style="font-size: 16px; font-weight: 700; color: #FFFFFF; margin-bottom: 12px;">
        ✨ What you can do with SafeBite:
      </div>

      <div class="feature-card">
        <div class="feature-title">📸 Instant AI Food Label Scanner</div>
        <p class="feature-desc">Snap any food package or nutrition facts table. Google Gemini Vision AI extracts calories, protein, carbs, fats, and analyzes ingredients in seconds.</p>
      </div>

      <div class="feature-card">
        <div class="feature-title">⚠️ Allergen & Harmful Additive Detector</div>
        <p class="feature-desc">Instantly spot artificial dyes, dangerous preservatives, excess sodium, and common allergens before you eat.</p>
      </div>

      <div class="feature-card">
        <div class="feature-title">🩺 Diabetic & Dietary Personalization</div>
        <p class="feature-desc">Tailor alerts to your specific health profile—Diabetic Safe, Low Carb, Keto, Gluten-Free, or Vegan. Get custom 0–100 Health Scores.</p>
      </div>

      <div class="feature-card">
        <div class="feature-title">💬 24/7 AI Nutritionist Chat</div>
        <p class="feature-desc">Ask real-time questions like <em>"Is this safe for my diet?"</em> or <em>"Suggest a healthier alternative"</em> with expert AI dietary guidance.</p>
      </div>

      <!-- Quick Start Guide -->
      <div style="font-size: 16px; font-weight: 700; color: #FFFFFF; margin-top: 24px; margin-bottom: 10px;">
        🚀 How to get started in 3 easy steps:
      </div>

      <div class="steps-container">
        <div class="step-item">
          <div class="step-number">1</div>
          <div class="step-text"><strong>Open SafeBite:</strong> Launch the app and tap the Camera Scan button.</div>
        </div>
        <div class="step-item">
          <div class="step-number">2</div>
          <div class="step-text"><strong>Capture Label:</strong> Point your camera at the Nutrition Facts or Ingredients list.</div>
        </div>
        <div class="step-item">
          <div class="step-number">3</div>
          <div class="step-text"><strong>Get Instant Insights:</strong> Review your Health Score, allergen warnings, and healthy alternatives!</div>
        </div>
      </div>

      <div class="pro-tip">
        💡 <strong>Pro Tip:</strong> Ensure good lighting and keep the nutrition table flat in frame for the most accurate Gemini Vision analysis.
      </div>

      <!-- CTA Button -->
      <div class="cta-container">
        <a href="https://safebite-g3fc.onrender.com" class="cta-button" target="_blank">
          Open SafeBite & Start Scanning →
        </a>
      </div>
    </div>

    <!-- Footer -->
    <div class="footer">
      <strong>SafeBite Health & Nutrition AI</strong><br>
      Eat Smarter. Live Healthier.<br>
      Questions or feedback? Reach us at <a href="mailto:safebitefoodanalyzer@gmail.com" style="color: #10B981; text-decoration: none;">safebitefoodanalyzer@gmail.com</a><br><br>
      You received this email because you registered an account with SafeBite.
    </div>
  </div>
</body>
</html>
"""


def get_welcome_email_text(username: Optional[str] = None) -> str:
    """
    Generates plain-text alternative of the Welcome Email for text-only clients.
    """
    display_name = username.strip() if username and username.strip() else "Health Explorer"
    return f"""Hello {display_name},

Welcome to SafeBite – AI Food Health Analyzer! 🥗

Your personal AI-powered food health companion is now ready. SafeBite helps you understand what's really in the food you eat, avoid harmful additives, and make confident health choices.

✨ What you can do with SafeBite:
1. 📸 Instant AI Label Scanner - Scan nutrition facts and ingredient tables with Gemini Vision AI.
2. ⚠️ Allergen & Additive Alerts - Detect hidden chemicals, artificial preservatives, and allergens.
3. 🩺 Diabetic & Diet Scores - Personalized food safety ratings for diabetes, keto, and clean diets.
4. 💬 24/7 AI Nutritionist - Ask questions and receive instant dietary guidance.

🚀 3 Easy Steps to Get Started:
1. Open the SafeBite app and tap the camera scan button.
2. Take a clear photo of any food package nutrition table or ingredients list.
3. Review your instant Health Score (0-100) and healthy alternatives!

💡 Pro Tip: Make sure the nutrition facts and ingredient list are well-lit and in focus.

Start scanning today: https://safebite-g3fc.onrender.com

Have questions or suggestions? Reach out to our nutrition team anytime at safebitefoodanalyzer@gmail.com.

Regards,
SafeBite Health & Nutrition Team
Eat Smarter. Live Healthier.
"""


def send_welcome_email(
    to_email: str,
    username: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Sends a rich, branded Welcome Email introducing SafeBite to the user.
    Returns (success: bool, error_message: Optional[str]).
    """
    clean_target = to_email.strip().lower()
    display_name = username.strip() if username and username.strip() else "Health Explorer"

    subject = f"Welcome to SafeBite, {display_name}! 🥗 Your AI Food Health Companion"
    plain_text = get_welcome_email_text(username=display_name)
    html_content = get_welcome_email_html(username=display_name)

    return _dispatch_email(
        to_email=clean_target,
        subject=subject,
        plain_text=plain_text,
        html_content=html_content,
        log_tag="Welcome Email"
    )
