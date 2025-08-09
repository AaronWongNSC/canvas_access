from canvas_access.canvas_object import CanvasObject
from canvas_access.submission import Submission
from canvas_access.util import GET_list, list_to_dict

class Student(CanvasObject):
    def __init__(self, Course, json_dict):
        self.inherit(Course)
        self.course_id = Course.id
        self.course_name = Course.name

        self.info_keys = ['sis_user_id', 'name']
        self.type = 'Student'

        super().__init__(json_dict)
    
    def __str__(self):
        return f'{self.type} [Course ID: {self.course_id}]: {self.id} \t {self.short_name} ({self.sis_user_id})'

    def get_submissions(self):
        url = self.base_api_url + f'/courses/{self.course_id}/students/submissions?per_page=100'
        params = {'student_ids[]': self.id}
        assignment_list = GET_list(self.session, self.auth, url, params = params)
        return list_to_dict(self, Submission, assignment_list)
