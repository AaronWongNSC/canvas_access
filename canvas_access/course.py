"""
Module for the Course CanvasObject for the canvas_access module. 
"""

from canvas_access.assignment import Assignment
from canvas_access.assignment_group import AssignmentGroup
from canvas_access.canvas_object import CanvasObject
from canvas_access.discussion import Discussion
from canvas_access.user import User
from canvas_access.util import GET_list, list_to_dict

class Course(CanvasObject):
    """
    Course CanvasObject for canvas_access.

    Attributes:
        Universal attributes: auth, base_api_url, session, tz
        General attributes: info_keys, lineage, type
        Other inherited attributes: None
        Course-level attributes:
            - Others obtained from API
    
    Methods:
        get_assignment(): Get an assignment within a course by assignment ID
        get_assignments(): Get all assignments within a course
        get_assignment_group(): Get a single assignment group by assignment group ID
        get_assignment_groups(): Get all assignment groups within a course
        get_discussion(): Get a single discussion within a course by ID
        get_discussion(): Get all discusions within a course
        get_user(): Get a single user within a course by user ID.
        get_users(): Get users within a course by category.
        start_conversation(): Create a new conversation.
    """

    def __init__(self, canvas, json_dict):
        self.inherit(canvas)

        super().__init__(json_dict)

        if 'name' not in self.__dict__.keys():
            self.name = 'N/A'
        self.info_keys = ['name']
        self.type = 'Course'

    def __str__(self):
        return f'{self.type}: {self.id} \t {self.name}'

    def get_assignment(self, assignment_id: int) -> Assignment:
        """
        Gets a single assignment from a course.

        Endpoint:
            v1/courses/{course_id}/assignments/{assignment_id}

        Args:
            assignment_id (int): The ID of the assignment.

        Returns:
            Assignment: A CanvasObject representing the assignment.
        """
        url = self.base_api_url + f'/courses/{self.id}/assignments/{assignment_id}'
        return Assignment(self, self.session.get(url, headers = self.auth).json())

    def get_assignments(self) -> dict[Assignment]:
        """
        Gets all assignments from a course.

        Endpoint:
            v1/courses/{course_id}/assignments/

        Args:
            None

        Returns:
            dict[Assignment]: A dictionary containing Assignment CanvasObjects whose keys are
                assignment IDs and whose values are the Assignment
        """
        url = self.base_api_url + f'/courses/{self.id}/assignments'
        params = {
            'per_page': 100
        }
        assignment_list = GET_list(self.session, self.auth, url, params = params)
        return list_to_dict(self, Assignment, assignment_list)

    def get_assignment_group(self, assignment_group_id):
        """
        Gets a single assignment group from a course.

        Endpoint:
            v1/courses/{course_id}/assignment_groups/{assignment_group_id}

        Args:
            assignment_group_id (int): The ID of the assignment group.

        Returns:
            AssignmentGroup: A CanvasObject representing the assignment group.
        """
        url = self.base_api_url + f'/courses/{self.id}/assignment_groups/{assignment_group_id}'
        return AssignmentGroup(self, self.session.get(url, headers = self.auth).json())

    def get_assignment_groups(self) -> dict[AssignmentGroup]:
        """
        Gets all assignment groups from a course.

        Endpoint:
            v1/courses/{course_id}/assignments_groups/

        Args:
            None

        Returns:
            dict[AssignmentGroup]: A dictionary containing AssignmentGroup CanvasObjects whose keys are
                assignment group IDs and whose values are the AssignmentGroup
        """
        url = self.base_api_url + f'/courses/{self.id}/assignment_groups'
        assignment_group_list = GET_list(self.session, self.auth, url)
        return list_to_dict(self, AssignmentGroup, assignment_group_list)

    def get_discussion(self, topic_id) -> Discussion:
        """
        Gets a single discussion from a course.

        Endpoint:
            v1/courses/{course_id}/discussion_topics/{topic_id}

        Args:
            topic_id (int): The ID of the discussion topic.

        Returns:
            Discussion: A CanvasObject representing the discussion.
        """
        url = self.base_api_url + f'/courses/{self.id}/discussion_topics/{topic_id}'
        return Discussion(self, self.session.get(url, headers = self.auth).json())

    def get_discussions(self) -> dict[Discussion]:
        """
        Gets all discussions from a course.

        Endpoint:
            v1/courses/{course_id}/discussion_topics/

        Args:
            None

        Returns:
            dict[Discussion]: A dictionary containing Discussion CanvasObjects whose keys are
                discussion IDs and whose values are the Discussion.
        """
        url = self.base_api_url + f'/courses/{self.id}/discussion_topics'
        params = {
            'per_page': 100
        }
        discussion_list = GET_list(self.session, self.auth, url, params = params)
        return list_to_dict(self, Discussion, discussion_list)

    def get_user(self, user_id: int) -> User:
        """
        Gets a single user from a course.

        Endpoint:
            v1/courses/{course_id}/users/{user_id}

        Args:
            user_id (int): The ID of the user.

        Returns:
            Discussion: A CanvasObject representing the discussion.
        """
        url = self.base_api_url + f'/courses/{self.id}/users/{user_id}'
        params = {
            'include[]': 'enrollments'
        }
        user = User(self, self.session.get(url, headers = self.auth, params = params).json())
        if user.enrollments[0]['type'] == 'StudentEnrollment':
            user.enrollment_type = 'student'
        elif user.enrollments[0]['type'] == 'TeacherEnrollment':
            user.enrollment_type = 'teacher'
        else:
            user.enrollment_type = 'ERROR'
        return user
        

    def get_users(self, enrollment_types: list[str] = ['student']) -> dict[User]:
        """
        Gets all user from a course within a certain enrollment type.

        Endpoint:
            v1/courses/{course_id}/users/{user_id}

        Args:
            user_id (int): The ID of the user.
            enrollment_type (list[str]): Controls the types of users to be retrieved.
                - Options: teacher, student, student_view (students plus the test_student),
                    ta, observer, designer

        Returns:
            Discussion: A CanvasObject representing the discussion.
        """
        url = self.base_api_url + f'/courses/{self.id}/users'
        user_list = []
        for enrollment_type in enrollment_types:
            params = {
                'per_page': 100,
                'enrollment_type[]': enrollment_type
            }
            temp_user_list = GET_list(self.session, self.auth, url, params = params)

            for user in temp_user_list:
                user['enrollment_type'] = enrollment_type
            
            user_list += temp_user_list
        return list_to_dict(self, User, user_list)
