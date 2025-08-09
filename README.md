Get data using the Canvas API. The data is dumped into dictionaries for easier access. Am I going to properly document this? Probably not.

## Basic Usage

```
from canvas_access.canvas import Canvas

API_URL = "https://campus.instructure.com"
API_KEY = "GetYourOwnKey"

session = Canvas(API_URL, API_KEY)
session.info()

courses = session.get_courses() # Generates a dictionary of all courses indexed by course numbers
course = session.get_course(course_id) # Generates a CanvasObject from the course information
```

## General Comments

* The CanvasObject is just a generic class for all things comning out of Canvas. It automatically loads the data from a GET into `__dict__` so that it can be accessed using the dot notation.
* It allows for loading in a timezone from `pytz` and will automatically create local time string formats of time objects.
* Use .info() and .all_info() to see the data in the fields.
* Child objects (Canvas -> Course) inherit data from the Parent object.

## Structure

* Canvas
  * Course
    * Assignment Group
    * Assignment
      * Submission
    * Student
      * Submission
