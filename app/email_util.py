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


class EmailSender:
    @staticmethod
    def send_welcome_email(receiver_email: str, user_name: str, role: str, reg_no: str, password: str):
        """
        Send a professional welcome email with login credentials.
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Welcome to the Department"
        msg["From"] = EMAIL_USERNAME
        msg["To"] = receiver_email

        # ✅ Professional HTML email (without image)
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; color: #333;">
            <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
              
              <h2 style="color: #2c3e50; text-align: center;">Welcome to the Department!</h2>
              
              <p>Dear <b>{user_name}</b>,</p>
              
              <p>
                We are delighted to welcome you as a <b>{role.capitalize()}</b> of the department. 
                Your account has been successfully created in our system.
              </p>
              
              <h3 style="color: #2c3e50; margin-top: 20px;">Your Login Credentials</h3>
              <p><b>Registration Number:</b> {reg_no}</p>
              <p><b>Temporary Password:</b> {password}</p>
              
              <p style="background: #f1f1f1; padding: 10px; border-radius: 6px; font-size: 14px; color: #555;">
                ⚠️ Please log in and change your password immediately after your first login for security reasons.
              </p>
              
              <p>
                If you encounter any difficulties, kindly contact the department’s IT support team for assistance.
              </p>
              
              <p style="margin-top: 30px;">Best regards,<br>
              <b>The Department Team</b></p>
              
            </div>
          </body>
        </html>
        """

        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                server.sendmail(EMAIL_USERNAME, receiver_email, msg.as_string())
            print(f"✅ Welcome email sent successfully to {receiver_email}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")



    @staticmethod
    def send_welcome_email_lecturer(receiver_email: str, lecturer_name: str, role: str, password: str) -> None:
        """
        Send a welcome email to a new lecturer with department logo.
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Welcome to the Department Faculty"
            msg["From"] = EMAIL_USERNAME
            msg["To"] = receiver_email

            html_content = f"""
            <html>
            <head></head>
            <body style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; 
                            border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <img src="{LECTURER_IMAGE_URL}" alt="Department Logo" style="max-width: 150px; margin-bottom: 20px;">
                    <h2 style="color: #2c3e50;">Welcome, {lecturer_name}!</h2>
                    <p style="font-size: 16px;">Your Department account has been successfully created.</p>
                    <p style="font-size: 16px;"><b>Designation:</b> {role.capitalize()}</p>
                    <p style="font-size: 16px; color: #27ae60;"><b>Password:</b> {password}</p>
                    <p style="font-size: 15px; line-height: 1.5;">
                        We look forward to your valuable contributions to our department's academic and research activities.
                    </p>
                    <p style="margin-top: 30px; font-weight: bold; color: #555;">Sincerely,<br>The Department Team</p>
                </div>
            </body>
            </html>
            """
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                server.sendmail(EMAIL_USERNAME, receiver_email, msg.as_string())

            print(f"✅ Email sent successfully to {receiver_email}")

        except Exception as e:
            print(f"❌ Failed to send email to {receiver_email}: {e}")



    @staticmethod
    def send_role_change_email(receiver_email: str, student_name: str, old_role: str, new_role: str):
        """
        Send a role change notification email with department logo.
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Role Change Notification"
        msg["From"] = EMAIL_USERNAME
        msg["To"] = receiver_email

        # ✅ Professional HTML email
        html_content = f"""
        <html>
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

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                server.sendmail(EMAIL_USERNAME, receiver_email, msg.as_string())
            print(f"✅ Role change email sent successfully to {receiver_email}")
        except Exception as e:
            print(f"❌ Failed to send role change email to {receiver_email}: {e}")



    @staticmethod
    def send_password_change_email(receiver_email: str, user_name: str, reg_no: str):
        """
        Send a password change notification email.
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Password Change Notification"
        msg["From"] = EMAIL_USERNAME
        msg["To"] = receiver_email

        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; color: #333;">
            <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
              
              <div style="text-align: center; margin-bottom: 20px;">
                <img src="{IMAGE_URL}" alt="Department Logo" style="max-width: 120px; pointer-events: none; user-select: none;" oncontextmenu="return false;">
              </div>
              
              <h2 style="color: #2c3e50; text-align: center;">Password Changed Successfully</h2>
              
              <p>Dear <b>{user_name}</b>,</p>
              
              <p>
                This is to notify you that the password for your account 
                (<b>{reg_no}</b>) has been changed successfully.
              </p>
              
              <p style="background: #f1f1f1; padding: 10px; border-radius: 6px; font-size: 14px; color: #555;">
                ⚠️ If you did not initiate this change, please contact the department's IT support immediately.
              </p>
              
              <p style="margin-top: 30px;">Best regards,<br>
              <b>The Department Team</b></p>
              
            </div>
          </body>
        </html>
        """

        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                server.sendmail(EMAIL_USERNAME, receiver_email, msg.as_string())
            print(f"✅ Password change email sent successfully to {receiver_email}")
        except Exception as e:
            print(f"❌ Failed to send password change email to {receiver_email}: {e}")


    @staticmethod
    def send_lecturer_password_change_email(receiver_email: str, lecturer_name: str):
        """
        Send a professional email notification to a lecturer when their password is changed.
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Password Change Notification"
        msg["From"] = EMAIL_USERNAME
        msg["To"] = receiver_email

        # ✅ Professional HTML email
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; 
                        border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                
                <img src="{LECTURER_IMAGE_URL}" alt="Department Logo" 
                     style="max-width: 150px; margin-bottom: 20px; pointer-events: none; user-select: none;" 
                     oncontextmenu="return false;">
                
                <h2 style="color: #2c3e50;">Hello {lecturer_name},</h2>
                
                <p style="font-size: 16px;">
                    We would like to inform you that your <b>Department Faculty account password</b> 
                    has been successfully updated.
                </p>
                
                <p style="font-size: 15px; line-height: 1.5; color: #555;">
                    ✅ If this change was made by you, no further action is required.<br>
                    ❌ If you did not request this change, please contact the system administrator immediately.
                </p>
                
                <p style="margin-top: 30px; font-weight: bold; color: #555;">
                    Sincerely,<br>The Department Team
                </p>
            </div>
          </body>
        </html>
        """

        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                server.sendmail(EMAIL_USERNAME, receiver_email, msg.as_string())
            print(f"✅ Lecturer password change email sent successfully to {receiver_email}")
        except smtplib.SMTPAuthenticationError:
            print("❌ SMTP Authentication failed. Check EMAIL_USERNAME or EMAIL_PASSWORD.")
        except smtplib.SMTPConnectError:
            print("❌ Unable to connect to SMTP server. Check SMTP_SERVER and SMTP_PORT.")
        except Exception as e:
            print(f"❌ Failed to send password update email to {receiver_email}: {e}")



    @staticmethod
    def send_student_otp_email(receiver_email: str, user_name: str, reg_no: str, otp: str):
        """
        Send a professional OTP email to a student for password reset.
        Uses SMTP and image settings from Config.
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Password Reset OTP"
        msg["From"] = Config.EMAIL_USERNAME
        msg["To"] = receiver_email

        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px;
                        border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
              
              <img src="{Config.IMAGE_URL}" alt="Department Logo"
                   style="max-width: 150px; margin-bottom: 20px; pointer-events: none; user-select: none;"
                   oncontextmenu="return false;">
              
              <h2 style="color: #2c3e50;">Hello {user_name},</h2>
              
              <p style="font-size: 16px;">
                We received a request to reset the password for your <b>student portal account</b>.
              </p>

              <p style="font-size: 16px;"><b>Registration Number:</b> {reg_no}</p>
              
              <p style="font-size: 18px; font-weight: bold; color: #e74c3c; margin: 20px 0;">
                🔑 Your One-Time Password (OTP) is:<br><br>
                <span style="font-size: 22px;">{otp}</span>
              </p>
              
              <p style="font-size: 15px; line-height: 1.5; color: #555;">
                ⏳ This OTP is valid for <b>5 minutes</b>.<br>
                ❌ If you did not request this reset, please ignore this email or contact support.
              </p>
              
              <p style="margin-top: 30px; font-weight: bold; color: #555;">
                Sincerely,<br>The Department Team
              </p>
            </div>
          </body>
        </html>
        """

        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(Config.EMAIL_USERNAME, Config.EMAIL_PASSWORD)
                server.sendmail(Config.EMAIL_USERNAME, receiver_email, msg.as_string())
            print(f"✅ OTP email sent successfully to {receiver_email}")
        except smtplib.SMTPAuthenticationError:
            print("❌ SMTP Authentication failed. Check EMAIL_USERNAME or EMAIL_PASSWORD.")
        except smtplib.SMTPConnectError:
            print("❌ Unable to connect to SMTP server. Check SMTP_SERVER and SMTP_PORT.")
        except Exception as e:
            print(f"❌ Failed to send OTP email to {receiver_email}: {e}")


    @staticmethod
    def send_lecturer_otp_email(receiver_email: str, user_name: str, otp: str):
        """
        Send a professional OTP email to a lecturer for password reset.
        SMTP and Image settings are pulled from Config.
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Password Reset OTP"
        msg["From"] = Config.EMAIL_USERNAME
        msg["To"] = receiver_email

        # ✅ Professional HTML body
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #fff; padding: 20px; 
                        border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                
                <img src="{Config.LECTURER_IMAGE_URL}" alt="Department Logo" 
                     style="max-width: 150px; margin-bottom: 20px; pointer-events: none; user-select: none;" 
                     oncontextmenu="return false;">
                
                <h2 style="color: #2c3e50;">Hello {user_name},</h2>
                
                <p style="font-size: 16px;">
                    We received a request to reset the password for your 
                    <b>faculty portal account</b>.
                </p>
                
                <p style="font-size: 18px; font-weight: bold; color: #e74c3c; margin: 20px 0;">
                    🔑 Your One-Time Password (OTP) is: <br><br>
                    <span style="font-size: 22px;">{otp}</span>
                </p>
                
                <p style="font-size: 15px; line-height: 1.5; color: #555;">
                    ⏳ This OTP is valid for <b>5 minutes</b>.<br>
                    ❌ If you did not request this reset, please ignore this email.
                </p>
                
                <p style="margin-top: 30px; font-weight: bold; color: #555;">
                    Sincerely,<br>The Department Team
                </p>
            </div>
          </body>
        </html>
        """

        msg.attach(MIMEText(html_content, "html"))

        # ✅ Send with error handling
        try:
            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(Config.EMAIL_USERNAME, Config.EMAIL_PASSWORD)
                server.sendmail(Config.EMAIL_USERNAME, receiver_email, msg.as_string())
            print(f"✅ OTP email sent successfully to {receiver_email}")
        except smtplib.SMTPAuthenticationError:
            print("❌ SMTP Authentication failed. Check EMAIL_USERNAME or EMAIL_PASSWORD.")
        except smtplib.SMTPConnectError:
            print("❌ Unable to connect to SMTP server. Check SMTP_SERVER and SMTP_PORT.")
        except Exception as e:
            print(f"❌ Failed to send OTP email to {receiver_email}: {e}")
