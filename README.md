Get data using the Canvas API. The data is dumped into dictionaries for easier access. This is more of a teacher-facing project than an admin-facing project. I'm mostly doing this to learn a bit more about how to use the API. The ideas I ended up with mirrored a lot of what the canvasapi package already does, and inadvertently had similar structures.

## Basic Usage

```python
from canvas_access.canvas import Canvas
from canvas_access.util import print_dict

API_URL = "https://campus.instructure.com"
API_KEY = "GetYourOwnKey"

canvas = Canvas(API_URL, API_KEY)
canvas.info()
canvas.all_info()

courses = session.get_courses() # Generates a dictionary of all courses indexed by course numbers
print_dict(courses)
course = courses[course_id] # Gets the Course CanvasObject from the dictionary

course = session.get_course(course_id) # Gets the Course CanvasObject from the API
```

## General Comments

* The CanvasObject is just a generic class for all things comning out of Canvas. It automatically loads the data from a GET into `__dict__` so that it can be accessed using the dot notation.
* It allows for loading in a timezone from `pytz` and will automatically create local time string formats of time objects.
* Use .info() and .all_info() to see the data in the fields.
* Child objects (Canvas -> Course) inherit data from the Parent object.

## Structures

Parent -> Child relationships

* Assignment -> Submission
* AssignmentGroup -> Assignment
* Canvas -> Course, Conversation
* Conversation -> Message
* Course -> Assignment, AssignmentGroup, Discussion, User
* Discussion -> Entry
* Entry -> None
* Message -> None
* Submission -> None
* User -> Conversation, Submission

Child <- Parent relationships
* Assignment <- AssignmentGroup, Course
* AssignmentGroup <- Course
* Canvas <- None
* Conversation <- Course, User
* Course <- Canvas
* Discussion <- Course
* Entry <- Discussion
* Message <- Conversation
* Submission <- Assignment, User
* User <- Course
