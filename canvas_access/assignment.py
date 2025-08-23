"""
Module for the Assignment CanvasObject for the canvas_access module. 
"""

from canvas_access.canvas_object import CanvasObject
from canvas_access.submission import Submission
from canvas_access.util import clean_html, GET_list, list_to_dict

class Assignment(CanvasObject):
    """
    Assignment CanvasObject for canvas_access.

    Attributes:
        Universal attributes: auth, base_api_url, session, tz,
        General attributes: info_keys, lineage, type
        Other inherited attributes: assignment_group_id
        Assignment-level attributes:
            - Others obtained from API
    
    Methods:
        get_submission(): Get a single submission for the assignment by user ID
        get_submissions(): Get all submissions for the assignment
    """

    def __init__(self, parent, json_dict):
        self.inherit(parent, ['assignment_group_id'])
        if parent.type == 'Course':
            self.course_id = parent.id
            self.course_name = parent.name
        elif parent.type == 'AssignmentGroup':
            self.assignment_group_id = parent.id
            self.add_assignment_group_info(parent)

        super().__init__(json_dict)

        self.description_text = clean_html(self.description)
        self.info_keys = ['course_id', 'course_name', 'assignment_group_id', 'name', 'points_possible', 'due_at_display']
        self.type = 'Assignment'
    
    def __str__(self):
        return f'{self.type} [Course ID: {self.course_id}; Assignment Group ID: {self.assignment_group_id})]: {self.id} \t {self.name}'

    def add_assignment_group_info(self, AssignmentGroup: 'AssignmentGroup') -> None: # type: ignore
        """
        Adds assignment group information from the assignment assignment. This is useful if the
        submission was obtained from the Course and the AssignmentGroup was pulled up after. This will first
        check the assignment group ID to ensure a match before generating the data

        Args:
            AssignmentGroup (AssignmentGroup): The AssignmentGroup corresponding to the assignment group

        Returns:
            None
        """
        if AssignmentGroup.id == self.assignment_group_id:
            self.assignment_group_weight = AssignmentGroup.group_weight
            self.assignment_group_name = AssignmentGroup.name
            self.course_id = AssignmentGroup.course_id
            self.course_name = AssignmentGroup.course_name

    def get_submission(self, user_id: int) -> Submission:
        """
        Gets a single submission for an assignment.

        Endpoint:
            v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}

        Args:
            user_id (int): The ID of the student.

        Returns:
            Submission: A CanvasObject representing the assignment.
        """
        url = self.base_api_url + f'/courses/{self.course_id}/assignments/{self.id}/submissions/{user_id}'
        return Submission(self, self.session.get(url, headers = self.auth).json())

    def get_submissions(self) -> dict[Submission]:
        """
        Gets all submissions for an assignment.

        Endpoint:
            v1/courses/{course_id}/assignments/{assignment_id}/submissions

        Args:
            None

        Returns:
            dict[Submissions]: A dictionary containing Submission CanvasObjects whose keys are
                submission IDs and whose values are the Submission
        """
        url = self.base_api_url + f'/courses/{self.course_id}/assignments/{self.id}/submissions'
        submission_list = GET_list(self.session, self.auth, url)
        return list_to_dict(self, Submission, submission_list)