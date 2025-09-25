from config import Config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ✅ Email configuration (explicitly set from Config)
SMTP_SERVER = Config.SMTP_SERVER
SMTP_PORT = int(Config.SMTP_PORT)
EMAIL_USERNAME = Config.EMAIL_USERNAME
EMAIL_PASSWORD = Config.EMAIL_PASSWORD
IMAGE_URL = Config.IMAGE_URL
LECTURER_IMAGE_URL = Config.LECTURER_IMAGE_URL


def send_welcome_email(receiver_email: str, user_name: str, role: str, reg_no: str, password: str) -> None:
    """
    Send a welcome email with department logo from IMAGE_URL.
    SMTP + Image settings are taken from Config.
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Welcome to the Department"
    msg["From"] = EMAIL_USERNAME
    msg["To"] = receiver_email

    # HTML body
    html_content = f"""
    <html>
    <head></head>
    <body style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <img src="{IMAGE_URL}" alt="Department Logo" 
                 style="max-width: 150px; margin-bottom: 20px; pointer-events: none; user-select: none;" 
                 oncontextmenu="return false;">
            <h2 style="color: #2c3e50;">Welcome, {user_name}!</h2>
            <p style="font-size: 16px;">We’re excited to let you know that your account has been successfully created.</p>
            <p style="font-size: 16px;"><b>Role:</b> {role}</p>
            <p style="font-size: 16px;"><b>Registration No:</b> {reg_no}</p>
            <p style="font-size: 16px; color: #27ae60;"><b>Password:</b> {password}</p>
            <p style="font-size: 15px; line-height: 1.5;">
                We are glad to have you as part of our community. Your contribution will play
                a big part in driving our department’s mission forward.
            </p>
            <p style="margin-top: 30px; font-weight: bold; color: #555;">Best regards,<br>The Department Team</p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    # Send the email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, receiver_email, msg.as_string())
        print(f"Email sent successfully to {receiver_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")



def send_welcome_email_lecturer(receiver_email: str, lecturer_name: str, role: str, password: str) -> None:
    """
    Send a welcome email to a new lecturer with department logo.
    Aligns with the lecturer registration system: uses proper name formatting and role.
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Welcome to the Department Faculty"
        msg["From"] = EMAIL_USERNAME
        msg["To"] = receiver_email

        # HTML body with proper formatting
        html_content = f"""
        <html>
        <head></head>
        <body style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <img src="{LECTURER_IMAGE_URL}" alt="Department Logo" style="max-width: 150px; margin-bottom: 20px;">
                <h2 style="color: #2c3e50;">Welcome, {lecturer_name}!</h2>
                <p style="font-size: 16px;">Your Department account has been successfully created.</p>
                <p style="font-size: 16px;"><b>Designation:</b> {role.capitalize()}</p>
                <p style="font-size: 16px; color: #27ae60;"><b>Password:</b> {password}</p>
                <p style="font-size: 15px; line-height: 1.5;">
                    We look forward to your valuable contributions to our department's academic and research activities. 
                    Your expertise will greatly enhance the growth and excellence of our institution.
                </p>
                <p style="margin-top: 30px; font-weight: bold; color: #555;">Sincerely,<br>The Department Team</p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_content, "html"))

        # Send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, receiver_email, msg.as_string())

        print(f"Email sent successfully to {receiver_email}")

    except Exception as e:
        print(f"Failed to send email to {receiver_email}: {e}")



def send_role_change_email(receiver_email: str, student_name: str, old_role: str, new_role: str) -> None:
    """
    Send a role change notification email with department logo from IMAGE_URL.
    SMTP + Image settings are taken from Config.
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Role Change Notification"
    msg["From"] = EMAIL_USERNAME
    msg["To"] = receiver_email

    # HTML body
    html_content = f"""
    <html>
    <head></head>
    <body style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <img src="{IMAGE_URL}" alt="Department Logo" 
                 style="max-width: 150px; margin-bottom: 20px; pointer-events: none; user-select: none;" 
                 oncontextmenu="return false;">
            <h2 style="color: #2c3e50;">Hello, {student_name}!</h2>
            <p style="font-size: 16px;">This is to inform you that your role in the Department has been updated.</p>
            <p style="font-size: 16px;"><b>Previous Role:</b> {old_role}</p>
            <p style="font-size: 16px; color: #27ae60;"><b>New Role:</b> {new_role}</p>
            <p style="font-size: 15px; line-height: 1.5;">
                If you have any questions or believe this change was made in error, please reach out
                to your lecturer or the department admin for clarification.
            </p>
            <p style="margin-top: 30px; font-weight: bold; color: #555;">Best regards,<br>The Department Team</p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    # Send the email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, receiver_email, msg.as_string())
        print(f"Role change email sent successfully to {receiver_email}")
    except Exception as e:
        print(f"Failed to send role change email: {e}")


def update_student_email(receiver_email: str, user_name: str, reg_no: str) -> None:
    """
    Send a notification email when a student updates their password.
    SMTP + Image settings are taken from Config.
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Password Change Notification"
    msg["From"] = EMAIL_USERNAME
    msg["To"] = receiver_email

    # HTML body
    html_content = f"""
    <html>
    <head></head>
    <body style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; 
                    border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <img src="{IMAGE_URL}" alt="Department Logo" 
                 style="max-width: 150px; margin-bottom: 20px; pointer-events: none; user-select: none;" 
                 oncontextmenu="return false;">
            <h2 style="color: #2c3e50;">Hello, {user_name}!</h2>
            <p style="font-size: 16px;">This is to inform you that your password has been successfully changed.</p>
            <p style="font-size: 16px;"><b>Registration No:</b> {reg_no}</p>
            <p style="font-size: 15px; line-height: 1.5; color: #e74c3c;">
                If you did not make this change, please contact the department support team immediately
                to secure your account.
            </p>
            <p style="margin-top: 30px; font-weight: bold; color: #555;">Best regards,<br>The Department Team</p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    # Send the email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, receiver_email, msg.as_string())
        print(f"Password change email sent successfully to {receiver_email}")
    except Exception as e:
        print(f"Failed to send password change email: {e}")


def update_lecturer_email(receiver_email: str, lecturer_name: str) -> None:
    """
    Send an email notification to a lecturer when their password is changed.
    SMTP + Image settings are taken from Config.
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Password Change Notification"
    msg["From"] = EMAIL_USERNAME
    msg["To"] = receiver_email

    # HTML body
    html_content = f"""
    <html>
    <head></head>
    <body style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <img src="{LECTURER_IMAGE_URL}" alt="Department Logo" style="max-width: 150px; margin-bottom: 20px;">
            <h2 style="color: #2c3e50;">Hello {lecturer_name},</h2>
            <p style="font-size: 16px;">We would like to inform you that your <b>Department Faculty account password</b> has been successfully updated.</p>
            
            <p style="font-size: 15px; line-height: 1.5; color: #555;">
                If this change was made by you, no further action is required.<br>
                If you did not request this change, please contact the system administrator immediately.
            </p>
            
            <p style="margin-top: 30px; font-weight: bold; color: #555;">Sincerely,<br>The Department Team</p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    # Send the email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, receiver_email, msg.as_string())
        print(f"Password update email sent successfully to {receiver_email}")
    except Exception as e:
        print(f"Failed to send update email: {e}")


def send_student_otp_email(receiver_email: str, user_name: str, reg_no: str, otp: str) -> None:
    """
    Send an OTP email to a student for password reset.
    SMTP + Image settings are taken from Config.
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Password Reset OTP"
    msg["From"] = EMAIL_USERNAME
    msg["To"] = receiver_email

    # HTML body
    html_content = f"""
    <html>
    <head></head>
    <body style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; 
                    border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <img src="{IMAGE_URL}" alt="Department Logo" 
                 style="max-width: 150px; margin-bottom: 20px; pointer-events: none; user-select: none;" 
                 oncontextmenu="return false;">
            <h2 style="color: #2c3e50;">Hello, {user_name}!</h2>
            <p style="font-size: 16px;">We received a request to reset your password for your account.</p>
            <p style="font-size: 16px;"><b>Registration No:</b> {reg_no}</p>
            <p style="font-size: 18px; font-weight: bold; color: #e74c3c; margin: 20px 0;">
                Your OTP is: {otp}
            </p>
            <p style="font-size: 15px; line-height: 1.5; color: #555;">
                This OTP is valid for <b>5 minutes</b>. <br>
                If you did not request this, please ignore this email.
            </p>
            <p style="margin-top: 30px; font-weight: bold; color: #555;">Best regards,<br>The Department Team</p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    # Send the email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, receiver_email, msg.as_string())
        print(f"OTP email sent successfully to {receiver_email}")
    except Exception as e:
        print(f"Failed to send OTP email: {e}")


def send_lecturer_otp_email(receiver_email: str, user_name: str, otp: str) -> None:
    """
    Send an OTP email to a lecturer for password reset.
    SMTP + Image settings are taken from Config.
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Password Reset OTP"
    msg["From"] = EMAIL_USERNAME
    msg["To"] = receiver_email

    # HTML body
    html_content = f"""
    <html>
    <head></head>
    <body style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; 
                    border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <img src="{LECTURER_IMAGE_URL}" alt="Department Logo" 
                 style="max-width: 150px; margin-bottom: 20px; pointer-events: none; user-select: none;" 
                 oncontextmenu="return false;">
            <h2 style="color: #2c3e50;">Hello, {user_name}!</h2>
            <p style="font-size: 16px;">We received a request to reset your password for your account.</p>
            <p style="font-size: 18px; font-weight: bold; color: #e74c3c; margin: 20px 0;">
                Your OTP is: {otp}
            </p>
            <p style="font-size: 15px; line-height: 1.5; color: #555;">
                This OTP is valid for <b>5 minutes</b>. <br>
                If you did not request this, please ignore this email.
            </p>
            <p style="margin-top: 30px; font-weight: bold; color: #555;">Best regards,<br>The Department Team</p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    # Send the email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, receiver_email, msg.as_string())
        print(f"OTP email sent successfully to {receiver_email}")
    except Exception as e:
        print(f"Failed to send OTP email to {receiver_email}: {e}")
