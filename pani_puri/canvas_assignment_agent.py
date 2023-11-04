import enum
import os

import openai
from canvasapi import Canvas
from instructor import OpenAISchema
from pydantic import Field

openai.api_key = os.environ.get("OPENAI_API_KEY")

CANVAS_API_URL = "https://canvas.ubc.ca/"
CANVAS_API_KEY = os.environ.get("CANVAS_API_KEY")

MATH317_COURSE_CODE = 125207

MATH300_COURSE_CODE = 125222

canvas = Canvas(CANVAS_API_URL, CANVAS_API_KEY)

math317 = canvas.get_course(MATH317_COURSE_CODE)
math300 = canvas.get_course(MATH300_COURSE_CODE)


class UniversityClass(str, enum.Enum):
    """Enumeration representing the university class I'm searching up."""

    MATH300 = "math300"
    MATH317 = "math317"


class AssignmentDetails(OpenAISchema):
    """
    Correctly extract assignment information
    """

    name: str = Field(..., description="Assignment's Name")
    course: UniversityClass = Field(
        ..., description="The University class this assignment is from"
    )


def parseAssignments(course_obj):
    """
    Parses a course object into a dictionary of assignment name and due date

    param course_obj (canvasapi.course.Course): course obj to return assignments for

    return: dictionary with assignment name as key and due date as value
    """
    assignment_list = list(course_obj.get_assignments())
    return dict(
        zip(
            map((lambda x: x.name), assignment_list),
            map((lambda x: x.due_at), assignment_list),
        )
    )


def getAssignments(course):
    """
    Parses a string into course object and calls parseAssignments

    param course (str): name of course

    return: dictionary with assignment name as key and due date as value
    """
    if course == "math300":
        return parseAssignments(math300)
    if course == "math317":
        return parseAssignments(math317)
    else:
        return "invalid course"


def findDue(dict_assignments, assignment):
    """
    given a dictionary with assignment name as key and due date as value, and an assignment, returns when assignment is due

    param dict_assignments (dict(str, str)): dictionary with name as key and due date as value
    param assignment (str): name of assignment

    return: due date as a string
    """
    for key in dict_assignments:
        if key.lower() == assignment.lower():
            return dict_assignments[key]

    return "Assignment not found"


def respond(question):
    """
    given a question, answer it by calling Canvas's API

    param question (str): question you want to ask

    return: response as a string
    """
    assignment_parse = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        functions=[AssignmentDetails.openai_schema],
        function_call={"name": AssignmentDetails.openai_schema["name"]},
        messages=[
            {
                "role": "system",
                "content": "Extract assignment details from my requests",
            },
            {"role": "user", "content": question},
        ],
    )

    assignment = AssignmentDetails.from_response(assignment_parse)

    ret = findDue(getAssignments(assignment.course.value), assignment.name)
    # print(ret)

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        functions=[AssignmentDetails.openai_schema],
        messages=[
            {
                "role": "system",
                "content": "Answer the request given the question and function response, giving the exact date and time. Give time in the current timezone in Vancouver, remembering that the given time is in UTC so you need to switch to the correct timezone. If assignment isn't found, tell the user that instead.",
            },
            {"role": "user", "content": question},
            {
                "role": "function",
                "name": AssignmentDetails.openai_schema["name"],
                "content": ret,
            },
        ],
    )

    return completion["choices"][0]["message"]["content"]


user_qn = input("What would you like to ask the assistant?\n")

print(respond(user_qn))
