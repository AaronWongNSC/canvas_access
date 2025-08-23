"""
Module for the User CanvasObject for the canvas_access module. 
"""

from canvas_access.canvas_object import CanvasObject
from canvas_access.conversation import Conversation
from canvas_access.submission import Submission
from canvas_access.util import GET_list, list_to_dict

class User(CanvasObject):
    """
    User CanvasObject for canvas_access.

    Attributes:
        Universal attributes: auth, base_api_url, session, tz
        General attributes: info_keys, lineage, type
        Other inherited attributes: Varies with parent CanvasObject
            Course: course_id, course_name
        Course-level attributes:
            - Others obtained from API
    
    Methods:
        get_submissions(): Get all submissions within a course.
        get_assignment_group(): Get a single assignment group by assignment group ID
        get_assignment_groups(): Get all assignment groups within a course
        get_discussion(): Get a single discussion within a course by ID
        get_discussion(): Get all discusions within a course
        get_user(): Get a single user within a course by user ID.
        get_users(): Get users within a course by category.
    """
    def __init__(self, parent, json_dict):
        self.inherit(parent)
        if parent.type == 'Course':
            self.course_id = parent.id
            self.course_name = parent.name

        super().__init__(json_dict)

        self.info_keys = ['sis_user_id', 'name']
        self.type = 'User'

    def __str__(self):
        return f'{self.type} [Course ID: {self.course_id}]: {self.id} \t {self.short_name} ({self.sis_user_id})'

    def get_submissions(self, course_id = None) -> dict[Submission]:
        """
        Gets all submissions from a user in a specific course. If no course is specified, it will try to use the students inherited course ID.

        Endpoint:
            v1/courses/{course_id}/students/submissions

        Args:
            course_id (int): If none is provided, it will be assumed that the User is already identified
                within a specific course.

        Returns:
            dict[Submission]: A dictionary containing Submission CanvasObjects whose keys are
                submission IDs and whose values are the Submission.
        """
        if self.enrollment_type != 'student':
            return {
                'error': 'Not a student'
            }

        if course_id == None:
            course_id = self.course_id
        url = self.base_api_url + f'/courses/{course_id}/students/submissions'
        params = {
            'per_page': 100,
            'student_ids[]': self.id
        }
        assignment_list = GET_list(self.session, self.auth, url, params = params)
        return list_to_dict(self, Submission, assignment_list)