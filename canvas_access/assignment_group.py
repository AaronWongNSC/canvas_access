"""
Module for the AssignmentGroup CanvasObject for the canvas_access module. 
"""

from canvas_access.assignment import Assignment
from canvas_access.canvas_object import CanvasObject
from canvas_access.util import GET_list, list_to_dict

class AssignmentGroup(CanvasObject):
    """
    Course CanvasObject for canvas_access.

    Attributes:
        Universal attributes: auth, base_api_url, session, tz
        General attributes: info_keys, lineage, type
        Other inherited attributs: course_id, course_name
        AssignmentGroup attributes:
            - Others obtained from API
    
    Methods:
        get_assignments(): Get all assignments in the assignment group
    """

    def __init__(self, course, json_dict):
        self.inherit(course)
        self.course_id = course.id
        self.course_name = course.name

        super().__init__(json_dict)

        self.info_keys = ['course_id', 'course_name', 'name', 'group_weight']
        self.type = 'AssignmentGroup'
    
    def __str__(self):
        return f'{self.type} [Course ID: {self.course_id}]: {self.id} \t {self.name}'

    def get_assignments(self) -> dict[Assignment]:
        """
        Gets all assignments from a course within the assignment_group.

        Endpoint:
            v1/courses/{course_id}/assignment_groups/{assignment_group_id}/assignments

        Args:
            None

        Returns:
            dict[Assignment]: A dictionary containing Assignment CanvasObjects whose keys are
                assignment IDs and whose values are the Assignment
        """
        url = self.base_api_url + f'/courses/{self.course_id}/assignment_groups/{self.id}/assignments'
        assignment_list = GET_list(self.session, self.auth, url)
        return list_to_dict(self, Assignment, assignment_list)
