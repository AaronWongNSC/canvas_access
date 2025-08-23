"""
Module for the Submission CanvasObject for the canvas_access module. 
"""

from canvas_access.canvas_object import CanvasObject

class Submission(CanvasObject):
    """
    Submission CanvasObject for canvas_access.

    Attributes:
        Universal attributes: auth, base_api_url, session, tz
        General attributes: info_keys, lineage, type
        Other inherited attributes: Varies with parent CanvasObject
            - Assignment: course_id, course_name, due_at (various versions), points_possible
            - User: TBD
        Course-level attributes:
            - Others obtained from API
    
    Methods:
        add_assignment_info(): Copy information from the Assignment to the Submission
        TODO: add_user_info():
    """

    def __init__(self, parent: CanvasObject, json_dict: dict):
        self.inherit(parent,
                     ['course_id', 'course_name', 'points_possible',
                      'due_at', 'due_at_dt', 'due_at_display', 'due_at_localtime'])
    
        super().__init__(json_dict)

        self.info_keys = ['course_id', 'assignment_group_id', 'assignment_id', 'assignment_name',
                        'user_id', 'user_name', 'score', 'assignment_points_possible', 'assignment_due_at_display', 'late', 'missing']
        self.type = 'Submission'

        if self.lineage[-1]['type'] == 'Assignment':
            self.add_assignment_info(parent)
        elif self.lineage[-1]['type'] == 'User':
            self.user_name = parent.name
   
    def __str__(self):
        return f'{self.type} (Course ID: {self.course_id}; Assignment ID: {self.assignment_id}; User ID: {self.user_id}]: {self.id}'
    
    def add_assignment_info(self, assignment: 'Assignment'): # type: ignore
        """
        Adds assignment information from assignment. This is useful if the submission
        was obtained from a User and the Assignment was pulled up after. This will first
        check the assignment ID to ensure a match before generating the data

        Args:
            Assignment (Assignment): The Assignment corresponding to the submission

        Returns:
            None
        """
        if assignment.id == self.assignment_id:
            for key in ['description', 'description_text',
                        'due_at', 'due_at_display', 'due_at_dt', 'due_at_localtime'
                        'group_id', 'html_url', 'name', 'points_possible']:
                if key in assignment.__dict__.keys():
                    self.__dict__['assignment_' + key] = assignment.__dict__[key]
            if self.score != None and 'assignment_points_possible' in self.__dict__.keys():
                if self.assignment_points_possible > 0:
                    self.__dict__['percent_score'] = self.score / self.assignment_points_possible * 100
                else:
                    self.__dict__['percent_score'] = 0.0
            else:
                self.__dict__['percent_score'] = 0.0

