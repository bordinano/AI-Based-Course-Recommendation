from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def send_email_smtp(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
    """
    Send email via SMTP.
    Returns True if successful, False otherwise.
    """
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.SMTP_FROM]):
        logger.warning("SMTP settings not fully configured, skipping email send")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email

        if text_content:
            msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_email_sendgrid(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
    """
    Send email via SendGrid.
    Returns True if successful, False otherwise.
    """
    if not settings.SENDGRID_API_KEY or not settings.SENDGRID_FROM:
        logger.warning("SendGrid settings not configured, skipping email send")
        return False

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content

        message = Mail(
            from_email=Email(settings.SENDGRID_FROM),
            to_emails=To(to_email),
            subject=subject,
            html_content=Content("text/html", html_content),
        )
        if text_content:
            message.content.append(Content("text/plain", text_content))

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)

        if 200 <= response.status_code < 300:
            logger.info(f"Email sent successfully to {to_email} via SendGrid")
            return True
        else:
            logger.error(f"SendGrid error: {response.status_code} - {response.body}")
            return False
    except Exception as e:
        logger.error(f"Failed to send email via SendGrid to {to_email}: {e}")
        return False


def send_results_email(to_email: str, student_name: str, results: dict) -> bool:
    """
    Send assessment results email to student.
    """
    if not settings.EMAIL_ENABLED:
        logger.info("Email sending is disabled (EMAIL_ENABLED=False)")
        return False

    # Generate email content
    subject = "Your Course Recommendation Results - Muntinlupa City College Guide"

    top_program = results.get("recommended_programs", [{}])[0]
    program_name = top_program.get("program_name", "N/A") if top_program else "N/A"
    compatibility = top_program.get("compatibility_score", "N/A") if top_program else "N/A"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #111827; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #cdffd8 0%, #94b9ff 100%); padding: 30px; border-radius: 16px 16px 0 0; text-align: center;">
            <h1 style="margin: 0; font-size: 28px; font-weight: bold; color: #111827;">Assessment Complete!</h1>
            <p style="margin: 10px 0 0; color: #374151;">Your personalized course recommendations are ready</p>
        </div>

        <div style="background: #fffdf2; padding: 30px; border-radius: 0 0 16px 16px; border: 1px solid #fde68a; border-top: none;">
            <p style="font-size: 16px;">Hi <strong>{student_name}</strong>,</p>

            <p style="font-size: 16px;">Thank you for completing the AI-Based Course Recommendation Assessment. Based on your responses, we've generated personalized course recommendations for universities in Muntinlupa City.</p>

            <div style="background: linear-gradient(135deg, #283d7a 0%, #50505a 100%); border-radius: 12px; padding: 24px; margin: 24px 0; text-align: center; color: white;">
                <p style="margin: 0 0 8px; font-size: 14px; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px;">Your Best Match</p>
                <h2 style="margin: 0 0 8px; font-size: 24px; font-weight: bold;">{program_name}</h2>
                <p style="margin: 0; font-size: 16px; opacity: 0.9;">Compatibility Score: <strong>{compatibility}%</strong></p>
            </div>

            <h3 style="font-size: 18px; color: #111827; margin: 24px 0 16px;">Other Recommended Programs</h3>
            <ul style="padding-left: 20px; margin: 0 0 24px;">
    """

    other_programs = results.get("recommended_programs", [])[1:4]
    for prog in other_programs:
        html_content += f"""
                <li style="margin-bottom: 8px;">
                    <strong>{prog.get('program_name', 'N/A')}</strong> — {prog.get('compatibility_score', 'N/A')}%
                    <br><small style="color: #6b7280;">{prog.get('explanation', '')}</small>
                </li>
        """

    html_content += """
            </ul>

            <h3 style="font-size: 18px; color: #111827; margin: 24px 0 16px;">Recommended Schools</h3>
            <ul style="padding-left: 20px; margin: 0 0 24px;">
    """

    schools = results.get("recommended_schools", [])[:5]
    for school in schools:
        inst_type = school.get("institution_type", "")
        badge_color = "#dbeafe" if inst_type == "Public" else "#f3e8ff"
        badge_text_color = "#1d4ed8" if inst_type == "Public" else "#7c3aed"
        html_content += f"""
                <li style="margin-bottom: 12px;">
                    <strong>{school.get('school_name', 'N/A')}</strong>
                    <span style="display: inline-block; background: {badge_color}; color: {badge_text_color}; padding: 2px 8px; border-radius: 9999px; font-size: 12px; font-weight: 600; margin-left: 8px;">{inst_type}</span>
                    <br><small style="color: #6b7280;">{school.get('program_offered', 'N/A')} — {school.get('address', 'N/A')}</small>
                    {f'<br><a href="{school.get("website_url")}" style="color: #283d7a;">Visit Website</a>' if school.get('website_url') else ''}
                </li>
        """

    html_content += """
            </ul>

            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 0 8px 8px 0; margin-top: 24px;">
                <p style="margin: 0; font-size: 14px; color: #92400e;">
                    <strong>Note:</strong> The recommended schools are limited to educational institutions within Muntinlupa City that offer the recommended program. Students are encouraged to verify admission requirements and program availability directly with the institution.
                </p>
            </div>

            <p style="margin-top: 32px; font-size: 14px; color: #6b7280;">
                Best regards,<br>
                <strong>Muntinlupa City College Guide Team</strong>
            </p>
        </div>

        <div style="text-align: center; padding: 20px; color: #9ca3af; font-size: 12px;">
            <p>This email was sent from the AI-Based Course Recommendation System.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Hi {student_name},

    Thank you for completing the AI-Based Course Recommendation Assessment. Based on your responses, we've generated personalized course recommendations for universities in Muntinlupa City.

    Your Best Match: {program_name} — Compatibility Score: {compatibility}%

    Other Recommended Programs:
    """

    for prog in other_programs:
        text_content += f"\n- {prog.get('program_name', 'N/A')} ({prog.get('compatibility_score', 'N/A')}%) — {prog.get('explanation', '')}"

    text_content += "\n\nRecommended Schools:\n"

    for school in schools:
        text_content += f"\n- {school.get('school_name', 'N/A')} ({school.get('institution_type', '')}) — {school.get('program_offered', 'N/A')} at {school.get('address', 'N/A')}"
        if school.get('website_url'):
            text_content += f"\n  Website: {school.get('website_url')}"

    text_content += """

    Note: The recommended schools are limited to educational institutions within Muntinlupa City that offer the recommended program. Students are encouraged to verify admission requirements and program availability directly with the institution.

    Best regards,
    Muntinlupa City College Guide Team
    """

    # Send via configured provider
    if settings.EMAIL_PROVIDER == "sendgrid":
        return send_email_sendgrid(to_email, subject, html_content, text_content)
    else:
        return send_email_smtp(to_email, subject, html_content, text_content)