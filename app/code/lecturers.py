from app.utils import *
from app.email_util import *
from flask import Flask, jsonify, Response
from flask_restful import Api, Resource, reqparse
from werkzeug.exceptions import BadRequest
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import random
import bcrypt   
import io


class RegisterLecturer(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("surname", type=str, required=True, help="Surname is required")
        self.parser.add_argument("first_name", type=str, required=True, help="First name is required")
        self.parser.add_argument("other_names", type=str, required=False)  # optional
        self.parser.add_argument("phone_number", type=str, required=True, help="Phone number is required")
        self.parser.add_argument("email", type=str, required=True, help="Email is required")
        self.parser.add_argument("gender", type=str, required=True, help="Gender is required")
        self.parser.add_argument("title", type=str, required=False)  # optional

    def post(self):
        args = self.parser.parse_args()

        # ✅ Normalize input
        surname = normalize_name(args["surname"])
        first_name = normalize_name(args["first_name"])
        other_names = normalize_name(args["other_names"]) if args.get("other_names") else None
        phone_number = normalize_phone(args["phone_number"])
        email = normalize_email(args["email"])
        gender = args["gender"].strip().lower()
        title = args.get("title")

        # ✅ Validate phone number
        if not is_valid_nigerian_number(phone_number):
            raise BadRequest("Invalid Nigerian phone number format")

        # ✅ Validate email
        if not is_valid_gmail(email):
            raise BadRequest("Invalid Gmail address")

        # ✅ Validate gender
        if gender not in ["male", "female"]:
            raise BadRequest("Gender must be either 'Male' or 'Female'")

        # ✅ Validate title
        if title:
            title = title.strip().capitalize()
            if title not in ["Dr", "Prof"]:
                raise BadRequest("Title must be either 'Dr' or 'Prof'")
        else:
            title = None  # default if not provided

        # ✅ Check duplicates
        if lecturers.find_one({"phone_number": phone_number}):
            raise BadRequest("A lecturer with this phone number already exists")

        if lecturers.find_one({"email": email}):
            raise BadRequest("A lecturer with this email already exists")

        # ✅ Default password (six zeros)
        default_password = "000000"

        # ✅ Hash the password
        hashed_password = bcrypt.hashpw(default_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # ✅ Save new lecturer
        new_lecturer = {
            "surname": surname,
            "first_name": first_name,
            "other_names": other_names,
            "phone_number": phone_number,
            "email": email,
            "gender": normalize_word(gender),
            "title": title,
            "role": "lecturer",
            "password": hashed_password
        }
        lecturers.insert_one(new_lecturer)

        # ✅ Build full name with/without title
        full_name = f"{surname} {first_name}" + (f" {other_names}" if other_names else "")
        lecturer_name = f"{title} {full_name}" if title else full_name

        # ✅ Send welcome email
        send_welcome_email_lecturer(
            receiver_email=email,
            lecturer_name=lecturer_name,
            role=new_lecturer["role"],
            password=default_password
        )

        return jsonify({
            "message": "Lecturer registered successfully, welcome email sent"
        })


# ✅ Register endpoint
api.add_resource(RegisterLecturer, "/api/register/lecturer")


class DemoteExco(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("email", type=str, required=True, help="Lecturer email is required")
        self.parser.add_argument("password", type=str, required=True, help="Lecturer password is required")
        self.parser.add_argument("reg_no", type=str, required=True, help="Student reg_no is required")

    def post(self):
        args = self.parser.parse_args()

        email = normalize_email(args["email"])
        password = args["password"]
        reg_no = args["reg_no"].strip().upper()

        # ✅ Check lecturer exists
        lecturer = lecturers.find_one({"email": email})
        if not lecturer:
            raise BadRequest("Lecturer not found")

        # ✅ Verify lecturer role
        if lecturer.get("role") != "lecturer":
            raise BadRequest("Only lecturers can perform this action")

        # ✅ Verify lecturer password
        if not bcrypt.checkpw(password.encode("utf-8"), lecturer["password"].encode("utf-8")):
            raise BadRequest("Invalid password")

        # ✅ Check if student exists
        student = members.find_one({"reg_no": reg_no})
        if not student:
            raise BadRequest("Student not found")

        # ✅ Validate student role
        student_role = student.get("role", "").lower()
        if student_role not in ["exco", "student"]:
            raise BadRequest("Invalid role for student. Must be 'exco' or 'student'")

        if student_role == "student":
            return jsonify({"message": "This user is already a student"})

        # ✅ Update role from exco → student
        members.update_one(
            {"reg_no": reg_no},
            {"$set": {"role": "Student"}}
        )

        # ✅ Send notification email to student
        student_email = student.get("email")
        student_name = f"{student.get('surname', '')} {student.get('first_name', '')}".strip()

        send_role_change_email(
            receiver_email=student_email,
            student_name=student_name,
            old_role="Exco",
            new_role="Student"
        )

        return jsonify({
            "message": f"Student with reg_no {reg_no} has been demoted from Exco to Student, and notified by email"
        })


# ✅ Add endpoint
api.add_resource(DemoteExco, "/api/demote/student")


class PromoteStudent(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("email", type=str, required=True, help="Lecturer email is required")
        self.parser.add_argument("password", type=str, required=True, help="Lecturer password is required")
        self.parser.add_argument("reg_no", type=str, required=True, help="Student reg_no is required")

    def post(self):
        args = self.parser.parse_args()

        email = normalize_email(args["email"])
        password = args["password"]
        reg_no = args["reg_no"].strip().upper()

        # ✅ Check lecturer exists
        lecturer = lecturers.find_one({"email": email})
        if not lecturer:
            raise BadRequest("Lecturer not found")

        # ✅ Verify lecturer role
        if lecturer.get("role") != "lecturer":
            raise BadRequest("Only lecturers can perform this action")

        # ✅ Verify lecturer password
        if not bcrypt.checkpw(password.encode("utf-8"), lecturer["password"].encode("utf-8")):
            raise BadRequest("Invalid password")

        # ✅ Check if student exists
        student = members.find_one({"reg_no": reg_no})
        if not student:
            raise BadRequest("Student not found")

        # ✅ Validate student role
        student_role = student.get("role", "").lower()
        if student_role not in ["exco", "student"]:
            raise BadRequest("Invalid role for student. Must be 'exco' or 'student'")

        # ✅ Check if already Exco
        if student_role == "exco":
            return jsonify({"message": "This student is already an Exco"})

        # ✅ Update role from student → exco
        members.update_one(
            {"reg_no": reg_no},
            {"$set": {"role": "Exco"}}
        )

        # ✅ Send notification email to student
        student_email = student.get("email")
        student_name = f"{student.get('surname', '')} {student.get('first_name', '')}".strip()

        send_role_change_email(
            receiver_email=student_email,
            student_name=student_name,
            old_role="Student",
            new_role="Exco"
        )

        return jsonify({
            "message": f"Student with reg_no {reg_no} has been promoted from Student to Exco, and notified by email"
        })


# ✅ Add endpoint
api.add_resource(PromoteStudent, "/api/promote/student")



class DownloadAllLecturers(Resource):
    def get(self):
        try:
            # Fetch lecturers, exclude _id and password
            lecturers_list = list(lecturers.find({}, {"_id": 0, "password": 0}))

            if not lecturers_list:
                return {"message": "No lecturers found"}, 404

            # Sort lecturers alphabetically by surname
            lecturers_list = sorted(lecturers_list, key=lambda s: s.get("surname", "").lower())

            # PDF in memory
            output = io.BytesIO()
            doc = SimpleDocTemplate(
                output,
                pagesize=landscape(letter),
                leftMargin=20,
                rightMargin=20,
                topMargin=20,
                bottomMargin=20,
            )
            elements = []

            styles = getSampleStyleSheet()
            elements.append(Paragraph("All Lecturers List", styles['Title']))

            # Add table headings (S/N + lecturer fields)
            headers = ["S/N"] + list(lecturers_list[0].keys())
            data = [headers]

            # Add rows with numbering
            for idx, lec in enumerate(lecturers_list, start=1):
                row = [idx] + [str(v) for v in lec.values()]
                data.append(row)

            # --- Fit table into page width ---
            page_width, _ = landscape(letter)
            usable_width = page_width - doc.leftMargin - doc.rightMargin

            # Divide usable width equally among columns
            col_count = len(headers)
            col_widths = [usable_width / col_count] * col_count

            # Use Paragraphs for wrapping text
            wrapped_data = []
            for row in data:
                wrapped_row = []
                for cell in row:
                    style = styles['Normal']
                    style.fontSize = 8
                    style.leading = 10
                    wrapped_row.append(Paragraph(str(cell), style))
                wrapped_data.append(wrapped_row)

            # Create table with fitted widths
            table = Table(wrapped_data, colWidths=col_widths, repeatRows=1)

            # Style
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),  # S/N center
                ("ALIGN", (1, 0), (-1, -1), "LEFT"),   # Other fields left
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),     # Smaller font
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]))

            elements.append(table)
            doc.build(elements)

            pdf_data = output.getvalue()
            output.close()

            # Prepare response
            response = Response(pdf_data, mimetype="application/pdf")
            response.headers["Content-Disposition"] = "attachment; filename=All_Lecturers.pdf"
            return response

        except Exception as e:
            return {"error": str(e)}, 500


# Route
api.add_resource(DownloadAllLecturers, "/lecturers/download-all")


class ChangeLecturerPassword(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("email", type=str, required=True, help="Email is required")
        self.parser.add_argument("previous_password", type=str, required=True, help="Previous password is required")
        self.parser.add_argument("new_password", type=str, required=True, help="New password is required")

    def post(self):
        args = self.parser.parse_args()

        # ✅ Normalize email
        email = normalize_email(args["email"])
        previous_password = args["previous_password"]
        new_password = args["new_password"]

        # ✅ Validate email
        if not is_valid_gmail(email):
            raise BadRequest("Invalid Gmail address")

        # 🔎 Check lecturer existence
        lecturer = lecturers.find_one({"email": email})
        if not lecturer:
            return {"message": "Lecturer not found"}, 404

        # 🔑 Verify old password
        if not bcrypt.checkpw(previous_password.encode("utf-8"), lecturer["password"].encode("utf-8")):
            return {"message": "Previous password is incorrect"}, 400

        # 🔒 Hash new password
        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # 📝 Update DB
        lecturers.update_one(
            {"email": email},
            {"$set": {"password": hashed_password}}
        )

        # ✅ Build lecturer full name
        full_name = f"{lecturer.get('surname')} {lecturer.get('first_name')}"
        if lecturer.get("other_names"):
            full_name += f" {lecturer['other_names']}"
        lecturer_name = f"{lecturer.get('title', '')} {full_name}".strip()

        # 📧 Notify lecturer (no new password shown)
        update_lecturer_email(receiver_email=email, lecturer_name=lecturer_name)

        return jsonify({
            "message": "Password updated successfully, email notification sent"
        })


# ✅ Register endpoint
api.add_resource(ChangeLecturerPassword, "/api/lecturer/change_password")


class ForgotPasswordLecturer(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("email", type=str, required=True, help="Lecturer email is required")

    def post(self):
        args = self.parser.parse_args()
        email = args["email"].strip().lower()

        # ✅ Check if lecturer exists
        lecturer = lecturers.find_one({"email": email})
        if not lecturer:
            raise BadRequest("No lecturer found with this email")

        # ✅ Check if there is an existing OTP that hasn't expired
        existing_otp_expiry = lecturer.get("otp_expiry")
        if existing_otp_expiry and existing_otp_expiry > datetime.utcnow():
            return jsonify({
                "message": f"An OTP has already been sent to {email}. Please check your email. "
                           "It will expire at "
                           f"{existing_otp_expiry.strftime('%Y-%m-%d %H:%M:%S UTC')}."
            })

        # ✅ Get lecturer name
        full_name = f"{lecturer.get('surname', '')} {lecturer.get('first_name', '')}".strip()
        if not full_name:
            full_name = "Lecturer"

        # ✅ Generate a new 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # ✅ Expiry time (5 minutes from now)
        expiry_time = datetime.utcnow() + timedelta(minutes=5)

        # ✅ Save OTP & expiry in DB
        lecturers.update_one(
            {"email": email},
            {"$set": {"reset_otp": otp, "otp_expiry": expiry_time}}
        )

        # ✅ Send OTP email
        send_lecturer_otp_email(
            receiver_email=email,
            user_name=full_name,
            otp=otp
        )

        return jsonify({
            "message": f"OTP sent to {email}. It will expire in 5 minutes."
        })


# ✅ Add endpoint to API
api.add_resource(ForgotPasswordLecturer, "/api/lecturer/forgot-password")


class LecturerResetPasswordUsingOTP(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("email", type=str, required=True, help="Lecturer email is required")
        self.parser.add_argument("otp", type=str, required=True, help="OTP is required")
        self.parser.add_argument("new_password", type=str, required=True, help="New password is required")

    def post(self):
        args = self.parser.parse_args()
        email = args["email"].strip().lower()
        otp = args["otp"].strip()
        new_password = args["new_password"].strip()

        # ✅ Check if lecturer exists
        lecturer = lecturers.find_one({"email": email})
        if not lecturer:
            raise BadRequest("No lecturer found with this email")

        # ✅ Check if OTP matches and is not expired
        stored_otp = lecturer.get("reset_otp")
        otp_expiry = lecturer.get("otp_expiry")

        if not stored_otp or stored_otp != otp:
            raise BadRequest("Invalid OTP")

        if not otp_expiry or otp_expiry < datetime.utcnow():
            raise BadRequest("OTP has expired. Please request a new one.")

        # ✅ Hash new password
        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # ✅ Update password in DB and remove OTP fields
        lecturers.update_one(
            {"email": email},
            {"$set": {"password": hashed_password},
             "$unset": {"reset_otp": "", "otp_expiry": ""}}
        )

        return jsonify({
            "message": "Lecturer password has been successfully reset."
        })


# ✅ Add endpoint
api.add_resource(LecturerResetPasswordUsingOTP, "/api/lecturer/reset-password-using-otp")

class LecturerLogin(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("email", type=str, required=True, help="Lecturer email is required")
        self.parser.add_argument("password", type=str, required=True, help="Password is required")

    def post(self):
        args = self.parser.parse_args()
        email = args["email"].strip().lower()
        password = args["password"].strip()

        # ✅ Check if lecturer exists
        lecturer = lecturers.find_one({"email": email})
        if not lecturer:
            return {"error": "Invalid email or password"}, 401

        # ✅ Verify password
        stored_password = lecturer.get("password")
        if not stored_password or not bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
            return {"error": "Invalid email or password"}, 401

        # Optional: Generate JWT token if needed
        # token = create_jwt_for_lecturer(lecturer)

        # ✅ Return lecturer info excluding password
        lecturer_info = {k: v for k, v in lecturer.items() if k not in ["_id", "password"]}

        return jsonify({
            "message": "Login successful",
            "lecturer": lecturer_info,
            # "token": token  # Uncomment if JWT is implemented
        })


# ✅ Add endpoint
api.add_resource(LecturerLogin, "/api/lecturer/login")

