from canvas_access.canvas_object import CanvasObject

class AssignmentGroup(CanvasObject):
    def __init__(self, Course, json_dict):
        self.inherit(Course)
        self.course_id = Course.id
        self.course_name = Course.name

        self.info_keys = ['course_id', 'course_name', 'name', 'group_weight']
        self.type = 'AssignmentGroup'

        super().__init__(json_dict)
    
    def __str__(self):
        return f'{self.type} [Course ID: {self.course_id}]: {self.id} \t {self.name}'