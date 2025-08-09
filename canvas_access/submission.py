from canvas_access.canvas_object import CanvasObject

class Submission(CanvasObject):
    def __init__(self, Parent, json_dict):
        self.inherit(Parent, ['course_id', 'course_name', 'points_possible', 'due_at', 'due_at_dt', 'due_at_localtime'])

        if Parent.type == 'Assignment':
            self.assignment_name = Parent.name
            self.assignment_id = Parent.id
        elif Parent.type == 'Student':
            self.user_name = Parent.name
    
        self.Parent = Parent.type
        self.info_keys = ['course_id', 'assignment_group_id', 'Parent', 'assignment_id', 'assignment_name',
                        'user_id', 'user_name', 'score', 'points_possible', 'posted_at', 'posted_at_localtime', 'late', 'missing']
        self.type = 'Submission'

        super().__init__(json_dict)
    
    def __str__(self):
        return f'{self.type} (Course ID: {self.course_id}; Assignment ID: {self.assignment_id}; User ID: {self.user_id}]: {self.id}'
    
    def add_Assignment_info(self, Assignment):
        if Assignment.id == self.assignment_id:
            self.assignment_description = Assignment.description
            self.assignment_due_at = Assignment.due_at
            self.assignment_due_at_dt = Assignment.due_at_dt
            self.assignment_due_at_localtime = Assignment.due_at_localtime
            self.assignment_group_id = Assignment.assignment_group_id
            self.assignment_html_url = Assignment.html_url
            self.assignment_name = Assignment.name
            self.assignment_points_possible = Assignment.points_possible

