import os

from canvasapi import Canvas

CANVAS_API_KEY = os.environ.get("CANVAS_API_KEY")
CANVAS_API_URL = "https://canvas.ubc.ca/"

canvas = Canvas(CANVAS_API_URL, CANVAS_API_KEY)

course = canvas.get_course(125015)

assignments = course.get_multiple_submissions()

for a in assignments:
    try:
        print(a.grade)
        # print(a)
        print(a.id)
        # print(course.get_assignment(a.id))
    except:
        print("execption")
