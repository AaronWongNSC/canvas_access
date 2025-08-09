import requests
from canvas_access.course import Course
from canvas_access.canvas_object import CanvasObject
from canvas_access.util import GET_list

class Canvas(CanvasObject):
    def __init__(self, url, key):
        self.info_keys = ['url', 'key_last_4', 'tz']
        self.type = 'Canvas'

        self.api_url = url + '/api/v1'
        self.auth = {"Authorization": "Bearer {}".format(key)}
        self.base_api_url = url + '/api/v1'
        self.key = key
        self.key_last_4 = key[-4:]
        self.session = requests.Session()
        self.tz = None
        self.url = url

    def __str__(self):
        return f'{self.type}'
    
    def get_course(self, course_id, json_dict = None):
        if json_dict == None:
            url = self.api_url + f'/courses/{course_id}'
            return Course(self, self.session.get(url, headers = self.auth).json())
        else:
            return Course(self, json_dict)

    def get_courses(self):
        url = self.api_url + '/courses?per_page=100'
        course_list = GET_list(self.session, self.auth, url)
        course_dict = {}
        for course in course_list:
            course_dict[course['id']] = self.get_course(course['id'], course)
        return course_dict
    
    def set_tz(self, tz):
        from pytz import timezone
        self.tz = timezone(tz)
        return