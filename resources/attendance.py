from flask_restful import Resource
from flask import request
from config.configDb import mydb
import traceback
from bson import json_util, ObjectId
import json
import datetime
import cv2
import numpy as np
import face_recognition
import os
import io
import pickle


attendanceCol = mydb['attendance']  # creating collection
courseCol = mydb['course']  # creating collection
model_col = mydb["model"]  # creating collection to save trained model


class Attendance(Resource):

    @staticmethod
    def post(date, course_id):
        try:
            reg_number = date
            course_id = ObjectId(course_id)
            today_date = str(datetime.date.today())

            # Verify Course id
            course = courseCol.find_one({"_id": course_id})
            if course is None:
                return "Course ID is invalid"

            current_attendance = attendanceCol.find_one({"courseId": course_id, "date": today_date})
            if current_attendance is None:
                new_attendance = [{reg_number: "p"}]

                attendance_dic = {
                    "date": today_date,
                    "attendance": new_attendance,
                    "courseId": course_id,
                }

                attendance_id = attendanceCol.insert_one(attendance_dic).inserted_id
                res = attendanceCol.find_one({"_id": attendance_id})

                res = json.loads(json_util.dumps(res))  # convert response to json
                res['_id'] = res['_id']['$oid']
                res['courseId'] = res['courseId']['$oid']

                return res

            old_attendance = current_attendance['attendance']
            new_attendance = {reg_number: "p"}

            if new_attendance not in old_attendance:
                old_attendance.append(new_attendance)

                query = {"courseId": course_id, "date": today_date}
                updated_attendance = {"$set": {"attendance": old_attendance}}
                new_res = attendanceCol.update_one(query, updated_attendance)

                print(new_res)
                return "updated"


        except Exception:
            return traceback.format_exc()

    @staticmethod
    def get(date, course_id):
        try:

            attendance = attendanceCol.find_one({"date": date, "courseId": ObjectId(course_id)})

            if attendance is None:
                return 'Date or Course id is invalid'

            attendance = json.loads(json_util.dumps(attendance))  # convert response to json
            attendance["_id"] = attendance["_id"]["$oid"]
            attendance["courseId"] = attendance["courseId"]["$oid"]

            return attendance

        except Exception:
            return 'Course Not Found'

    @staticmethod
    def delete(date, course_id):

        try:
            # find teacher by email.
            attendance = attendanceCol.find_one({"date": date, "courseId": ObjectId(course_id)})

            if attendance is None:
                return 'Attendance not found'

            attendance = attendanceCol.delete_one({"date": date, "courseId": ObjectId(course_id)})

            return attendance.deleted_count

        except Exception:
            return traceback.format_exc()


class CoursesAttendance(Resource):

    @staticmethod
    def get(course_id):
        try:
            courses_attendance = attendanceCol.find({"courseId": ObjectId(course_id)})  # get all courses_attendance
            courses_attendance = json.loads(json_util.dumps(courses_attendance))  # convert response to json

            for attendance in courses_attendance:
                attendance['_id'] = attendance['_id']['$oid']
                attendance["courseId"] = attendance["courseId"]["$oid"]

            return courses_attendance

        except Exception:
            return traceback.format_exc()


    # @staticmethod
    # def put(course_id):
    #     try:
    #         data = request.json
    #         date = str(datetime.date.today())
    #
    #         # Verify Course id
    #         course = courseCol.find_one({"_id": ObjectId(course_id)})
    #         if course is None:
    #             return "Course ID is invalid"
    #
    #         old_attendance = attendanceCol.find({"courseId": ObjectId(course_id), "date": date})
    #
    #         attendance_dic = {
    #             "date": str(datetime.date.today()),
    #             "attendance": data["attendance"],
    #             "courseId": ObjectId(data["courseId"]),
    #         }
    #
    #         attendance_id = attendanceCol.insert_one(attendance_dic).inserted_id
    #         res = attendanceCol.find_one({"_id": attendance_id})
    #
    #         res = json.loads(json_util.dumps(res))  # convert response to json
    #         res['_id'] = res['_id']['$oid']
    #         res['courseId'] = res['courseId']['$oid']
    #
    #         return res
    #
    #     except Exception:
    #         return traceback.format_exc()


