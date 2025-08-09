from canvas_access.canvas_object import CanvasObject
from canvas_access.submission import Submission
from canvas_access.util import GET_list, list_to_dict

class Assignment(CanvasObject):
    def __init__(self, Course, json_dict):
        self.inherit(Course, ['assignment_group_id'])
        self.course_id = Course.id
        self.course_name = Course.name

        self.info_keys = ['course_id', 'course_name', 'assignment_group_id', 'name', 'points_possible', 'due_at', 'due_at_localtime']
        self.type = 'Assignment'

        super().__init__(json_dict)

        self.api_url = self.base_api_url + f'/courses/{self.course_id}/assignments/{self.id}'
    
    def __str__(self):
        return f'{self.type} [Course ID: {self.course_id}; Assignment Group ID: {self.assignment_group_id})]: {self.id} \t {self.name}'

    def get_submission(self, student_id):
        url = self.api_url + f'/submissions/{student_id}'
        return Submission(self, self.session.get(url, headers = self.auth).json())

    def get_submissions(self):
        url = self.api_url + '/submissions'
        student_list = GET_list(self.session, self.auth, url)
        return list_to_dict(self, Submission, student_list)