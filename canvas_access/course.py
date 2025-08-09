from canvas_access.assignment import Assignment
from canvas_access.assignment_group import AssignmentGroup
from canvas_access.canvas_object import CanvasObject
from canvas_access.student import Student
from canvas_access.util import GET_list, list_to_dict

class Course(CanvasObject):
    def __init__(self, Canvas, json_dict):
        self.inherit(Canvas)

        self.info_keys = ['name']
        self.type = 'Course'

        self.__dict__['name'] = 'N/A'

        super().__init__(json_dict)

        self.api_url = self.base_api_url + f'/courses/{self.id}'

    def __str__(self):
        return f'{self.type}: {self.id} \t {self.name}'

    def get_assignment(self, assignment):
        url = self.api_url + f'/assignments/{assignment}'
        return Assignment(self, self.session.get(url, headers = self.auth).json())

    def get_assignments(self):
        url = self.api_url + '/assignments?per_page=100'
        assignment_list = GET_list(self.session, self.auth, url)
        return list_to_dict(self, Assignment, assignment_list)
    
    def get_assignments_by_group(self, assignment_group_id):
        url = self.api_url + f'/assignment_groups/{assignment_group_id}/assignments'
        assignment_list = GET_list(self.session, self.auth, url)
        return list_to_dict(self, Assignment, assignment_list)

    def get_assignment_group(self, assignment_group_id):
        url = self.api_url + f'/assignment_groups/{assignment_group_id}'
        return AssignmentGroup(self, self.session.get(url, headers = self.auth).json())

    def get_assignment_groups(self):
        url = self.api_url + '/assignment_groups'
        assignment_group_list = GET_list(self.session, self.auth, url)
        return list_to_dict(self, AssignmentGroup, assignment_group_list)

    def get_student(self, student_id):
        url = self.api_url + f'/users/{student_id}'
        return Student(self, self.session.get(url, headers = self.auth).json())

    def get_students(self):
        url = self.api_url + '/students'
        student_list = GET_list(self.session, self.auth, url)
        return list_to_dict(self, Student, student_list)