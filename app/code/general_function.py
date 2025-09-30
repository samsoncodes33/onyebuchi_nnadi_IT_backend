from app.utils import *
from flask import Flask, request
from flask_restful import Api, Resource
import datetime

from flask import Flask, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import datetime


class Announcement(Resource):
    def post(self):
        data = request.get_json()
        phone_number = data.get("phone_number")
        announcement_text = data.get("announcement", "").strip()

        if not phone_number or not announcement_text:
            return {"error": "phone_number and announcement are required"}, 400

        # Find the user in members collection
        member = members.find_one({"phone_number": phone_number})

        if not member:
            return {"error": "Member not found"}, 404

        role = member.get("role", "").lower()
        allowed_roles = ["exco", "lecturer"]

        if role not in allowed_roles:
            return {"error": "Access denied: only Exco or Lecturer can create announcements"}, 403

        # Extract student name
        surname = member.get("surname", "")
        first_name = member.get("first_name", "")
        other_names = member.get("other_names", "")
        full_name = " ".join([surname, first_name, other_names]).strip()

        # Check for duplicate announcement
        existing_announcement = announcement.find_one({
            "announcement_text": announcement_text
        })

        if existing_announcement:
            return {"error": "This announcement has already been posted"}, 409

        # Store announcement in MongoDB
        announcement_doc = {
            "phone_number": phone_number,
            "role": role,
            "student_name": full_name,
            "announcement_text": announcement_text,
            "announcement": f"{full_name} says: {announcement_text}",
            "created_at": datetime.datetime.utcnow()
        }
        announcement.insert_one(announcement_doc)

        return {"message": "Announcement posted successfully"}, 201


# Add resource to API
api.add_resource(Announcement, "/announcement")


class GetAllMembersAndCount(Resource):
    def get(self):
        try:            
            all_members_cursor = members.find({}, {"_id": 0, "password": 0})
            
            # Convert datetime fields to string
            all_members = []
            for member in all_members_cursor:
                for key, value in member.items():
                    if isinstance(value, (datetime.datetime, datetime.date)):
                        member[key] = value.isoformat()
                all_members.append(member)

            # Count excos (case-insensitive)
            total_excos = members.count_documents({"role": {"$regex": "^exco$", "$options": "i"}})
            
            # Count students (case-insensitive)
            total_students = members.count_documents({"role": {"$regex": "^student$", "$options": "i"}})
            
            # Count all members
            total_members = len(all_members)

            return {
                "members": all_members,
                "summary": {
                    "total_excos": total_excos,
                    "total_students": total_students,
                    "total_members": total_members
                }
            }, 200
        except Exception as e:
            return {"error": str(e)}, 500

api.add_resource(GetAllMembersAndCount, "/members/stats")


class GetAnnouncement(Resource):
    def get(self):
        # Fetch all announcements from the database
        all_announcements = list(announcement.find({}, {"_id": 0}))  # Exclude MongoDB _id

        if not all_announcements:
            return {"message": "No announcements found"}, 404

        # Convert datetime objects to ISO format strings
        for ann in all_announcements:
            if "created_at" in ann:
                ann["created_at"] = ann["created_at"].isoformat()

        # Sort by creation date (most recent first)
        all_announcements.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return {"announcements": all_announcements}, 200

# Add resource to API
api.add_resource(GetAnnouncement, "/get/announcement")


from flask import request
from flask_restful import Resource

class GetStudentsByGender(Resource):
    def post(self):
        try:
            # Ensure JSON body
            if not request.is_json:
                return {"error": "Request body must be JSON"}, 400

            data = request.get_json(silent=True)
            gender = data.get("gender", "").strip().lower()
            if gender not in ["male", "female"]:
                return {"error": "Invalid gender. Provide 'male' or 'female'."}, 400

            # Fetch students filtered by gender
            students_by_gender = list(members.find(
                {"gender": {"$regex": f"^{gender}$", "$options": "i"}},
                {"_id": 0, "password": 0}  # Exclude sensitive fields
            ))

            if not students_by_gender:
                return {"message": f"No students found for gender: {gender}"}, 404

            # Optionally sort alphabetically by surname
            students_by_gender.sort(key=lambda s: s.get("surname", "").lower())

            return {"students": students_by_gender}, 200

        except Exception as e:
            return {"error": str(e)}, 500

# Route
api.add_resource(GetStudentsByGender, "/students/by-gender")
