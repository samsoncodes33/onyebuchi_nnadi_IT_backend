from app.utils import *
from app.email_util import *
from flask import Flask, jsonify, Response, request
from flask_restful import Api, Resource, reqparse
from werkzeug.exceptions import BadRequest
import bcrypt   
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from datetime import datetime, timedelta
import random
import io, os


class Register(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("surname", type=str, required=True, help="Surname is required")
        self.parser.add_argument("first_name", type=str, required=True, help="First name is required")
        self.parser.add_argument("other_names", type=str, required=False)  # optional
        self.parser.add_argument("admission_type", type=str, required=True, help="Admission type is required")
        self.parser.add_argument("phone_number", type=str, required=True, help="Phone number is required")
        self.parser.add_argument("email", type=str, required=True, help="Email is required")
        self.parser.add_argument("gender", type=str, required=True, help="Gender is required")
        self.parser.add_argument("role", type=str, required=True, help="Role is required")
        self.parser.add_argument("reg_no", type=str, required=True, help="Registration number is required")

    def post(self):
        args = self.parser.parse_args()

        # Normalize input
        surname = normalize_name(args["surname"])
        first_name = normalize_name(args["first_name"])
        other_names = normalize_name(args["other_names"]) if args.get("other_names") else None
        admission_type = args["admission_type"].strip().lower()
        phone_number = normalize_phone(args["phone_number"])
        email = normalize_email(args["email"])
        gender = args["gender"].strip().lower()
        role = args["role"].strip().lower()
        reg_no = args["reg_no"].strip().upper()

        # ✅ Validate admission type
        valid_admission_types = ["utme", "direct entry", "transfer admission"]
        if admission_type not in valid_admission_types:
            raise BadRequest(f"Admission type must be one of {valid_admission_types}")

        # ✅ Validate phone number
        if not is_valid_nigerian_number(phone_number):
            raise BadRequest("Invalid Nigerian phone number format")

        # ✅ Validate email format
        if not is_valid_gmail(email):
            raise BadRequest("Invalid Gmail address")

        # ✅ Check duplicate email
        if members.find_one({"email": email}):
            raise BadRequest("A user with this email already exists")

        # ✅ Validate gender
        if gender not in ["male", "female"]:
            raise BadRequest("Gender must be either 'Male' or 'Female'")

        # ✅ Validate role
        if role not in ["student", "exco"]:
            raise BadRequest("Role must be one of ['Student', 'Exco']")

        # ✅ Validate Reg No format
        if not reg_no.startswith("2022/"):
            raise BadRequest("Registration number must start with '2022/'")
        if "/" not in reg_no[4:]:
            raise BadRequest("Registration number must contain '/' after the first 4 digits")
        if len(reg_no) > 11:
            raise BadRequest("Registration number must not exceed 11 characters")

        # ✅ Check duplicate reg no
        if members.find_one({"reg_no": reg_no}):
            raise BadRequest("A user with this registration number already exists")

        # ✅ Default password (always six zeros)
        default_password = "000000"

        # ✅ Hash the password before saving
        hashed_password = bcrypt.hashpw(default_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Save new user
        new_user = {
            "surname": surname,
            "first_name": first_name,
            "other_names": other_names,
            "admission_type": normalize_word(admission_type),
            "phone_number": phone_number,
            "email": email,
            "gender": normalize_word(gender),
            "role": normalize_word(role),
            "reg_no": reg_no,
            "password": hashed_password
        }
        members.insert_one(new_user)

        # Send welcome email
        full_name = f"{surname} {first_name}" + (f" {other_names}" if other_names else "")
        EmailSender.send_welcome_email(
            receiver_email=email,
            user_name=full_name,
            role=new_user["role"],
            reg_no=new_user["reg_no"],
            password=default_password
        )

        return jsonify({
            "message": "User registered successfully, welcome email sent"
        })


# Register endpoint
api.add_resource(Register, "/api/register")



class DownloadStudents(Resource):
    def get(self):
        students = list(members.find({}, {"_id": 0, "password": 0}))
        
        if not students:
            return {"message": "No students found"}, 404

        output = io.BytesIO()
        doc = SimpleDocTemplate(
            output,
            pagesize=landscape(letter),
            leftMargin=15,
            rightMargin=15,
            topMargin=15,
            bottomMargin=15
        )
        elements = []

        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]
        normal_style.fontSize = 9
        normal_style.leading = 11
        normal_style.wordWrap = 'CJK'

        # Title
        elements.append(Paragraph("026 Students", styles['Title']))
        elements.append(Spacer(1, 10))

        # Table headers
        headers = ["S/N"] + list(students[0].keys())
        data = [headers]

        # Build table rows with proper order and wrapping
        for idx, s in enumerate(students, start=1):
            row = [Paragraph(str(idx), normal_style)]
            for key in students[0].keys():
                value = s.get(key, "")
                row.append(Paragraph(str(value), normal_style))
            data.append(row)

        # Calculate page width
        page_width = doc.pagesize[0] - doc.leftMargin - doc.rightMargin

        # Assign column widths carefully
        col_widths = []
        for col in headers:
            if col.lower() in ["s/n"]:
                col_widths.append(1.3)  # S/N wide enough for 4 digits
            elif "email" in col.lower() or "address" in col.lower() or "name" in col.lower():
                col_widths.append(4.0)  # allow wrapping
            elif "phone" in col.lower():
                col_widths.append(2.5)
            else:
                col_widths.append(2.0)

        total_weight = sum(col_widths)
        scaled_widths = [(w / total_weight) * page_width for w in col_widths]

        table = Table(data, colWidths=scaled_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
            ("TOPPADDING", (0, 0), (-1, 0), 5),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ]))

        elements.append(table)
        doc.build(elements)

        pdf_data = output.getvalue()
        output.close()

        downloads_path = os.path.join(os.getcwd(), "Downloads")
        os.makedirs(downloads_path, exist_ok=True)
        file_path = os.path.join(downloads_path, "026 Students.pdf")
        with open(file_path, "wb") as f:
            f.write(pdf_data)

        response = Response(pdf_data, mimetype="application/pdf")
        response.headers["Content-Disposition"] = "attachment; filename=026 Students.pdf"
        return response

# Route
api.add_resource(DownloadStudents, "/students/download")



class DownloadSortedStudents(Resource):
    def get(self):
        # Fetch students, exclude _id and password
        students = list(members.find({}, {"_id": 0, "password": 0}))
        if not students:
            return {"message": "No students found"}, 404

        # Sort students alphabetically by surname
        students = sorted(students, key=lambda s: s.get("surname", "").lower())

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
        normal_style = styles["Normal"]
        normal_style.fontSize = 9
        normal_style.leading = 11
        normal_style.wordWrap = 'CJK'

        # Title
        elements.append(Paragraph("026 Students List", styles['Title']))
        elements.append(Spacer(1, 10))

        # Table headers
        headers = ["S/N"] + list(students[0].keys())
        data = [headers]

        # Add rows with numbering in header order
        for idx, s in enumerate(students, start=1):
            row = [idx]
            for key in students[0].keys():
                row.append(s.get(key, ""))
            data.append(row)

        # Calculate page width
        page_width = doc.pagesize[0] - doc.leftMargin - doc.rightMargin

        # Assign column widths carefully
        col_widths = []
        for col in headers:
            if col.lower() in ["s/n"]:
                col_widths.append(1.3)  # S/N wide enough for 4 digits
            elif "email" in col.lower() or "address" in col.lower() or "name" in col.lower():
                col_widths.append(4.0)  # allow wrapping
            elif "phone" in col.lower():
                col_widths.append(2.5)
            else:
                col_widths.append(2.0)

        total_weight = sum(col_widths)
        scaled_widths = [(w / total_weight) * page_width for w in col_widths]

        # Wrap all cell data with Paragraph
        wrapped_data = []
        for row in data:
            wrapped_row = []
            for cell in row:
                wrapped_row.append(Paragraph(str(cell), normal_style))
            wrapped_data.append(wrapped_row)

        # Create table
        table = Table(wrapped_data, colWidths=scaled_widths, repeatRows=1)

        # Style table
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),   # S/N center
            ("ALIGN", (1, 0), (-1, -1), "LEFT"),    # other fields left
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        elements.append(table)
        doc.build(elements)

        pdf_data = output.getvalue()
        output.close()

        # Prepare response
        response = Response(pdf_data, mimetype="application/pdf")
        response.headers["Content-Disposition"] = "attachment; filename=026 Students.pdf"
        return response


# Route
api.add_resource(DownloadSortedStudents, "/students/download-sorted")



class DownloadExcos(Resource):
    def get(self):
        # Fetch excos only, exclude _id and password
        excos = list(members.find(
            {"role": {"$regex": "^exco$", "$options": "i"}},
            {"_id": 0, "password": 0}
        ))
        if not excos:
            return {"message": "No excos found"}, 404

        # Sort excos alphabetically by surname
        excos = sorted(excos, key=lambda e: e.get("surname", "").lower())

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
        elements.append(Paragraph("026 Excos List", styles['Title']))

        # Add table headings (S/N + exco fields)
        headers = ["S/N"] + list(excos[0].keys())
        data = [headers]

        # Add rows with numbering
        for idx, e in enumerate(excos, start=1):
            row = [idx] + [str(v) for v in e.values()]
            data.append(row)

        # --- Fit table into page width ---
        page_width, _ = landscape(letter)
        usable_width = page_width - doc.leftMargin - doc.rightMargin

        # Divide usable width equally among columns
        col_count = len(headers)
        col_widths = [usable_width / col_count] * col_count

        # Use Paragraphs for wrapping text
        wrapped_data = []
        for r, row in enumerate(data):
            wrapped_row = []
            for c, cell in enumerate(row):
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
        response.headers["Content-Disposition"] = "attachment; filename=026_Excos.pdf"
        return response


# Route
api.add_resource(DownloadExcos, "/excos/download")


class DownloadMembersByGender(Resource):
    def post(self):
        try:
            # Check content type
            if not request.is_json:
                return {"error": "Request body must be JSON and not empty"}, 400

            # Parse JSON body
            data = request.get_json(silent=True)
            if not data or "gender" not in data or not data["gender"].strip():
                return {"error": "A data field 'gender' is required and should not be empty"}, 400

            gender = data["gender"].lower()
            if gender not in ["male", "female"]:
                return {"error": "Invalid gender. Please provide 'male' or 'female'."}, 400

            # Fetch all members filtered by gender
            members_by_gender = list(members.find(
                {"gender": {"$regex": f"^{gender}$", "$options": "i"}},
                {"_id": 0, "password": 0}
            ))
            if not members_by_gender:
                return {"message": f"No members found for gender: {gender}"}, 404

            # Sort alphabetically by surname
            members_by_gender = sorted(members_by_gender, key=lambda m: m.get("surname", "").lower())

            # PDF setup
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
            normal_style = styles["Normal"]
            normal_style.fontSize = 9
            normal_style.leading = 11
            normal_style.wordWrap = 'CJK'

            elements.append(Paragraph(f"026 Members List - {gender.capitalize()}", styles['Title']))
            elements.append(Spacer(1, 10))

            # Table headers
            headers = ["S/N"] + list(members_by_gender[0].keys())
            data = [headers]

            # Table rows
            for idx, m in enumerate(members_by_gender, start=1):
                row = [idx]
                for key in members_by_gender[0].keys():
                    row.append(m.get(key, ""))
                data.append(row)

            # Calculate page width
            page_width = doc.pagesize[0] - doc.leftMargin - doc.rightMargin

            # Assign relative column widths
            col_widths = []
            for col in headers:
                if col.lower() == "s/n":
                    col_widths.append(1.3)   # wide enough for 4 digits
                elif "name" in col.lower() or "email" in col.lower() or "address" in col.lower():
                    col_widths.append(4.0)   # wider columns
                elif "phone" in col.lower():
                    col_widths.append(2.5)
                else:
                    col_widths.append(2.0)   # default small-medium

            total_weight = sum(col_widths)
            scaled_widths = [(w / total_weight) * page_width for w in col_widths]

            # Wrap all data in Paragraphs
            wrapped_data = []
            for row in data:
                wrapped_row = [Paragraph(str(cell), normal_style) for cell in row]
                wrapped_data.append(wrapped_row)

            # Create table
            table = Table(wrapped_data, colWidths=scaled_widths, repeatRows=1)

            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),   # S/N center
                ("ALIGN", (1, 0), (-1, -1), "LEFT"),    # other fields left
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]))

            elements.append(table)
            doc.build(elements)

            pdf_data = output.getvalue()
            output.close()

            response = Response(pdf_data, mimetype="application/pdf")
            response.headers["Content-Disposition"] = f"attachment; filename=026_Members_{gender}.pdf"
            return response

        except Exception as e:
            return {"error": str(e)}, 500


# Route
api.add_resource(DownloadMembersByGender, "/members/download-by-gender")



class DownloadGroupedMembers(Resource):
    def post(self):
        try:
            # Validate request content type
            if not request.is_json:
                return {"error": "Request must be JSON"}, 400

            data = request.get_json()

            # Validate input parameters
            course_title = data.get("course_title")
            group_size = data.get("group_size")

            if not course_title or not str(course_title).strip():
                return {"error": "Course title is required"}, 400

            if not group_size or not str(group_size).isdigit():
                return {"error": "Group size must be a valid number"}, 400

            group_size = int(group_size)
            if group_size <= 0:
                return {"error": "Group size must be greater than zero"}, 400

            # Fetch members, exclude _id and password
            members_list = list(members.find({}, {"_id": 0, "password": 0}))

            if not members_list:
                return {"message": "No members found"}, 404

            # Sort members alphabetically by surname
            members_list = sorted(members_list, key=lambda s: s.get("surname", "").lower())

            # Split into groups
            groups = [
                members_list[i:i + group_size]
                for i in range(0, len(members_list), group_size)
            ]

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

            # Add course title at the top
            elements.append(Paragraph(f"{course_title} - Grouping", styles['Title']))
            elements.append(Spacer(1, 12))

            # Loop through each group and create a table
            for group_index, group in enumerate(groups, start=1):
                elements.append(Paragraph(f"Group {group_index}", styles['Heading2']))
                elements.append(Spacer(1, 6))

                # Table headers (S/N + member fields)
                headers = ["S/N"] + list(group[0].keys())
                data = [headers]

                # Add rows
                for idx, member in enumerate(group, start=1):
                    row = [idx] + [str(v) for v in member.values()]
                    data.append(row)

                # --- Fit table into page width ---
                page_width, _ = landscape(letter)
                usable_width = page_width - doc.leftMargin - doc.rightMargin
                col_count = len(headers)
                col_widths = [usable_width / col_count] * col_count

                # Wrap text in cells
                wrapped_data = []
                for row in data:
                    wrapped_row = []
                    for cell in row:
                        style = styles['Normal']
                        style.fontSize = 8
                        style.leading = 10
                        wrapped_row.append(Paragraph(str(cell), style))
                    wrapped_data.append(wrapped_row)

                # Create table
                table = Table(wrapped_data, colWidths=col_widths, repeatRows=1)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                    ("ALIGN", (1, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ]))

                elements.append(table)
                elements.append(Spacer(1, 20))

            doc.build(elements)

            pdf_data = output.getvalue()
            output.close()

            # Response
            response = Response(pdf_data, mimetype="application/pdf")
            response.headers["Content-Disposition"] = f"attachment; filename={course_title}_Groups.pdf"
            return response

        except Exception as e:
            return {"error": str(e)}, 500


# Route
api.add_resource(DownloadGroupedMembers, "/members/download-groups")


class ChangePassword(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("reg_no", type=str, required=True, help="Registration number is required")
        self.parser.add_argument("previous_password", type=str, required=True, help="Previous password is required")
        self.parser.add_argument("new_password", type=str, required=True, help="New password is required")

    def post(self):
        args = self.parser.parse_args()

        # Normalize input
        reg_no = args["reg_no"].strip().upper()
        previous_password = args["previous_password"]
        new_password = args["new_password"]

        # ✅ Check if student exists
        student = members.find_one({"reg_no": reg_no})
        if not student:
            raise BadRequest("Student with this registration number does not exist")

        # ✅ Verify previous password
        if not bcrypt.checkpw(previous_password.encode("utf-8"), student["password"].encode("utf-8")):
            raise BadRequest("Previous password is incorrect")

        # ✅ Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # ✅ Update password
        members.update_one(
            {"reg_no": reg_no},
            {"$set": {"password": hashed_password}}
        )

        # ✅ Send change password email notification
        full_name = f"{student.get('surname', '')} {student.get('first_name', '')}".strip()
        EmailSender.send_password_change_email(
            receiver_email=student["email"],
            user_name=full_name,
            reg_no=student["reg_no"]
        )

        return {
            "message": "Password changed successfully, notification email sent"
        }, 200


# Register endpoint
api.add_resource(ChangePassword, "/api/change-password")


class ForgotPasswordStudent(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            "reg_no", type=str, required=True, help="Registration number is required"
        )

    def post(self):
        args = self.parser.parse_args()
        reg_no = args["reg_no"].strip().upper()

        # ✅ Check if student exists
        student = members.find_one({"reg_no": reg_no})
        if not student:
            raise BadRequest("No student found with this registration number")

        # ✅ Get student email
        email = student.get("email")
        if not email:
            raise BadRequest("This student has no email on record")

        # ✅ Check if there is an existing OTP that hasn't expired
        existing_otp_expiry = student.get("otp_expiry")
        if existing_otp_expiry and existing_otp_expiry > datetime.utcnow():
            return jsonify({
                "status": "pending",
                "message": (
                    f"An OTP has already been sent to {email}. "
                    "Please check your email. "
                    f"It will expire at {existing_otp_expiry.strftime('%Y-%m-%d %H:%M:%S UTC')}."
                )
            })

        # ✅ Generate a new 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # ✅ Expiry time (5 minutes from now)
        expiry_time = datetime.utcnow() + timedelta(minutes=5)

        # ✅ Save OTP & expiry in DB
        members.update_one(
            {"reg_no": reg_no},
            {"$set": {"reset_otp": otp, "otp_expiry": expiry_time}}
        )

        # ✅ Send OTP email
        EmailSender.send_student_otp_email(
            receiver_email=email,
            user_name=student.get("full_name", "Student"),
            reg_no=reg_no,
            otp=otp
        )

        return jsonify({
            "status": "success",
            "message": f"OTP sent to {email}. It will expire in 5 minutes."
        })


# ✅ Add endpoint to API
api.add_resource(ForgotPasswordStudent, "/api/student/forgot-password")



class StudentResetPasswordUsingOTP(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("reg_no", type=str, required=True, help="Student registration number is required")
        self.parser.add_argument("otp", type=str, required=True, help="OTP is required")
        self.parser.add_argument("new_password", type=str, required=True, help="New password is required")

    def post(self):
        args = self.parser.parse_args()
        reg_no = args["reg_no"].strip().upper()
        otp = args["otp"].strip()
        new_password = args["new_password"].strip()

        # ✅ Check if student exists
        student = members.find_one({"reg_no": reg_no})
        if not student:
            raise BadRequest("No student found with this registration number")

        # ✅ Check if OTP matches and is not expired
        stored_otp = student.get("reset_otp")
        otp_expiry = student.get("otp_expiry")

        if not stored_otp or stored_otp != otp:
            raise BadRequest("Invalid OTP")

        if not otp_expiry or otp_expiry < datetime.utcnow():
            raise BadRequest("OTP has expired. Please request a new one.")

        # ✅ Hash new password
        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # ✅ Update password in DB and remove OTP fields
        members.update_one(
            {"reg_no": reg_no},
            {"$set": {"password": hashed_password},
             "$unset": {"reset_otp": "", "otp_expiry": ""}}
        )

        return jsonify({
            "message": "Student password has been successfully reset."
        })


# ✅ Add endpoint
api.add_resource(StudentResetPasswordUsingOTP, "/api/student/reset-password-using-otp")


class StudentLogin(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("reg_no", type=str, required=True, help="Registration number is required")
        self.parser.add_argument("password", type=str, required=True, help="Password is required")

    def post(self):
        args = self.parser.parse_args()
        reg_no = args["reg_no"].strip().upper()
        password = args["password"].strip()

        # ✅ Check if student exists
        student = members.find_one({"reg_no": reg_no})
        if not student:
            raise BadRequest("Invalid registration number or password")

        # ✅ Verify password
        stored_password = student.get("password")
        if not stored_password or not bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
            raise BadRequest("Invalid registration number or password")

        # Optional: Generate JWT token
        # token = create_jwt_for_student(student)  # implement JWT generation separately if needed

        # ✅ Return student info (excluding password)
        student_info = {k: v for k, v in student.items() if k != "password" and k != "_id"}

        return jsonify({
            "message": "Login successful",
            "student": student_info,
            # "token": token  # include if JWT is implemented
        })


# ✅ Add endpoint
api.add_resource(StudentLogin, "/api/student/login")



class RegisterStudentNoMail(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("surname", type=str, required=True, help="Surname is required")
        self.parser.add_argument("first_name", type=str, required=True, help="First name is required")
        self.parser.add_argument("other_names", type=str, required=False)  # optional
        self.parser.add_argument("admission_type", type=str, required=True, help="Admission type is required")
        self.parser.add_argument("phone_number", type=str, required=True, help="Phone number is required")
        self.parser.add_argument("email", type=str, required=True, help="Email is required")
        self.parser.add_argument("gender", type=str, required=True, help="Gender is required")
        self.parser.add_argument("role", type=str, required=True, help="Role is required")
        self.parser.add_argument("reg_no", type=str, required=True, help="Registration number is required")

    def post(self):
        args = self.parser.parse_args()

        # Normalize input
        surname = normalize_name(args["surname"])
        first_name = normalize_name(args["first_name"])
        other_names = normalize_name(args["other_names"]) if args.get("other_names") else None
        admission_type = args["admission_type"].strip().lower()
        phone_number = normalize_phone(args["phone_number"])
        email = normalize_email(args["email"])
        gender = args["gender"].strip().lower()
        role = args["role"].strip().lower()
        reg_no = args["reg_no"].strip().upper()

        # ✅ Validate admission type
        valid_admission_types = ["utme", "direct entry", "transfer admission"]
        if admission_type not in valid_admission_types:
            raise BadRequest(f"Admission type must be one of {valid_admission_types}")

        # ✅ Validate phone number
        if not is_valid_nigerian_number(phone_number):
            raise BadRequest("Invalid Nigerian phone number format")

        # ✅ Validate email format
        if not is_valid_gmail(email):
            raise BadRequest("Invalid Gmail address")

        # ✅ Check duplicate email
        if members.find_one({"email": email}):
            raise BadRequest("A user with this email already exists")

        # ✅ Validate gender
        if gender not in ["male", "female"]:
            raise BadRequest("Gender must be either 'Male' or 'Female'")

        # ✅ Validate role
        if role not in ["student", "exco"]:
            raise BadRequest("Role must be one of ['Student', 'Exco']")

        # ✅ Validate Reg No format
        if not reg_no.startswith("2022/"):
            raise BadRequest("Registration number must start with '2022/'")
        if "/" not in reg_no[4:]:
            raise BadRequest("Registration number must contain '/' after the first 4 digits")
        if len(reg_no) > 11:
            raise BadRequest("Registration number must not exceed 11 characters")

        # ✅ Check duplicate reg no
        if members.find_one({"reg_no": reg_no}):
            raise BadRequest("A user with this registration number already exists")

        # ✅ Default password (always six zeros)
        default_password = "000000"

        # ✅ Hash the password before saving
        hashed_password = bcrypt.hashpw(default_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Save new user
        new_user = {
            "surname": surname,
            "first_name": first_name,
            "other_names": other_names,
            "admission_type": normalize_word(admission_type),
            "phone_number": phone_number,
            "email": email,
            "gender": normalize_word(gender),
            "role": normalize_word(role),
            "reg_no": reg_no,
            "password": hashed_password
        }
        members.insert_one(new_user)

        return jsonify({
            "message": "Student registered successfully (no email sent)"
        })


# ✅ Register endpoint
api.add_resource(RegisterStudentNoMail, "/api/v1/register_student_no_mail")


class SortedStudentsSummary(Resource):
    def get(self):
        # Fetch students, exclude _id and password
        students = list(members.find({}, {"_id": 0, "password": 0}))
        if not students:
            return {"message": "No students found"}, 404

        # Sort students alphabetically by surname
        students_sorted = sorted(students, key=lambda s: s.get("surname", "").lower())

        # Count male and female separately
        male_count = sum(1 for s in students_sorted if s.get("gender", "").lower() == "male")
        female_count = sum(1 for s in students_sorted if s.get("gender", "").lower() == "female")

        # Total students
        total_students = len(students_sorted)

        response_data = {
            "total_students": total_students,
            "male": male_count,
            "female": female_count,
            "students": students_sorted  # keep the sorted students
        }

        return response_data, 200


# Route
api.add_resource(SortedStudentsSummary, "/students/summary-sorted")


class StudentViewAllLecturers(Resource):
    def get(self):
        try:
            # Fetch all lecturers from the collection
            lecturers = list(student_view_lecturers.find(
                {},
                {"_id": 0}  # Exclude MongoDB's default _id field
            ))

            if not lecturers:
                return {"message": "No lecturers found"}, 404

            # Optional: sort alphabetically by lecturer name
            lecturers.sort(key=lambda l: l.get("name", "").lower())

            return {"lecturers": lecturers}, 200

        except Exception as e:
            return {"error": str(e)}, 500


# Route
api.add_resource(StudentViewAllLecturers, "/Student/view_all_lecturers")
