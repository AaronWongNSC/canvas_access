"""
Grade_bundle classes for use with canvas_access.

Classes:
    AssignmentCluster: A class containing a list of assignments that are clustered together plus additional data.
    GradingBundle: A class of StudentPortfolios plus additional data.
    StudentPortfolio: A class of submissions from a single student plus additional data.
"""

import pandas as pd

from canvas_access.assignment import Assignment
from canvas_access.course import Course
from canvas_access.user import User
from canvas_access.util import GET_list, list_to_dict

class AssignmentCluster:
    """
    A collection of assignments that are grouped together for some reason, such as assignment groups or other types of related assignments.

    Attributes:
        assignment_ids (list[int]): A list of assignment_ids to be included in the cluster.
        name (str): The name of the assignment cluster.
        weight (float): The amount of weight of the cluster. This value is used with the weight_clusters() function.
    """
    def __init__(self, name: str, assignment_ids: list[int], weight: float = None):
        self.name = name
        self.assignment_ids = assignment_ids
        self.weight = weight

    def __str__(self):
        return f'{self.name}\t{self.weight}\t{self.assignment_ids}'

class GradingBundle:
    """
    A collection of StudentPortfolios plus additional data.

    Attributes:
        assignment_ids (list(int)): The list of assignment_ids.
        assignment (dict(Assignment)): A dictionary of assignments for the course indexed by assignment_id.
        portfolios (dict(StudentPortfolio)): A dictionary of student portfolios indexed by student_id.
        student_ids (list(int)): A list of student_ids.
        students (dict[User]): A dictionary of students for the bundle indexed by student_id
        type (str): Type of object for display in __str__.
    
    Methods:
        None
    """
    def __init__(self, course: 'Course', assignments: 'dict[Assignment]', students: 'dict[User]'): # type: ignore
        self.assignment_ids = list(assignments.keys())
        self.assignments = assignments
        self.portfolios = {}
        self.student_ids = list(students.keys())
        self.students = students
        self.type = 'GradingBundle'

        # Load the student submission data
        student_count = 0
        for student_id, student in students.items():
            student_count += 1
            print(f'Getting submissions for student {student_count} of {len(self.student_ids)} ({student.name})')
            self.portfolios[student_id] = StudentPortfolio(course, student, assignments)

class StudentPortfolio:
    """
    Student portfolio of work and data.

    Attributes:
        course_id (int): Course ID of the course.
        id (int): User ID for the student.
        submissions (dict[Submission]): A dictionary of submissions indexed by assignment_id.
        type (str): Type of object for display in __str__.
    
    Methods:
        None
    """
    def __init__(self, course: Course, user: User, assignments: dict[Assignment]):
        self.course_id = course.id
        self.course_name = course.name
        self.student_id = user.id
        self.student_name = user.name
        self.student_NSHE = user.sis_user_id
        self.type = 'StudentPortfolio'

        submissions = user.get_submissions(course.id)
        self.submissions = {
            submission.assignment_id: submission for _, submission in submissions.items()
        }
        for assignment_id, assignment in assignments.items():
            self.submissions[assignment_id].add_assignment_info(assignment)
    
    def __str__(self):
        print(f'{self.type} (Course: {self.course_name}): {self.student_id} \t{self.student_name} ({self.student_NSHE})')