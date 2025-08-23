"""
Module for the base level CanvasObject for the canvas_access module. 
"""

import requests
from canvas_access.conversation import Conversation
from canvas_access.course import Course
from canvas_access.canvas_object import CanvasObject
from canvas_access.util import GET_list, list_to_dict

class Canvas(CanvasObject):
    """
    Base level login for canvas_access

    Attributes:
        Universal attributes that will always be inherited by sub-objects:
            auth (dict): Canvas authorization header.
            base_api_url (str): Base API URL for Canvas REST API.
            session (requests.Session): Protocol used for HTTP-stuff.
            tz (str): pytz timezone string (ie, 'America/Los_Angeles').

        General attributes:
            info_keys (list[str]): Keys to display with .info().
            lineage (list[dict]): Keeps track of the CanvasObject lineage
            type (str): The name of the type of CanvasObject. This is somewhat
                redundant with the lineage.

        Canvas-level attributes:
            id (int): Empty attribute to avoid errors later
            key (str): Canvas API Key
            key_last_4 (str): Last 4 display for the key        
            url (str): Base URL for the Canvas instance
    
    Methods:
        get_conversations(): Gets conversations based on various parameters
        get_conversation(): Gets a single Conversation from the ID
        get_courses(): Gets all courses for the user 
        get_course(): Gets a specific course from either a json dictionary or a course ID
        set_tz(): Sets the timezone for the session
    """

    def __init__(self, canvas_url, key):
        self.auth = {'Authorization': 'Bearer {}'.format(key)}
        self.base_api_url = canvas_url + '/api/v1'
        self.session = requests.Session()
        self.tz = None

        self.id = None
        self.key = key
        self.key_last_4 = key[-4:]
        self.lineage = []
        self.url = canvas_url

        self.info_keys = ['url', 'key_last_4', 'tz']
        self.type = 'Canvas'

    def __str__(self):
        return f'{self.type}: {self.base_api_url}'
    
    def get_conversation(self, conversation_id) -> Conversation:
        """
        Creates a Conversation CanvasObject based on the conversation ID.
        
        Endpoint (when used):
            v1/conversations/{conversation_id}

        Args:
            conversation_id (int): The conversation ID of the course.

        Returns:
            Conversation: The Conversation corresdonding to the conversation ID
        """
        url = self.base_api_url + f'/conversations/{conversation_id}'
        return Conversation(self, self.session.get(url, headers = self.auth).json())


    def get_conversations(self,
                          count: int = 25,
                          filter: list[str] = None,
                          scope: list[str] = ['read_and_unread'],
                          parent: CanvasObject = None) -> dict[Conversation]:
        """
        Gets conversations semi-intelligently with arguments.

        Endpoint:
            v1/conversations

        Args:
            count (int): Sets the number of most recent items per API call. Maximum 100. If set to 0, this will
                get ALL conversations. Note that if this is done at the Canvas level, it might take a while. This
                is typically less concerning at the Course or User level.
            filter (list[str]): Applies filters to the search. Note that object types must be identified,
                such as cousre_123 and user_123. If providing a parent CanvasObject, those search parameters
                will be set automatically.
            scope (list[str]): The API call will run once for each scope.
                read_and_unread: Default search returns read and unread conversation.
                unread: Returns unread conversations.
                starred: Returns starred messages.
                archived: Returns archived messages.
                sent: Returns sent messages. Note that sent messages that hvae no responses will be found here.

        Returns:
            dict[Conversation]: A dictionary whose keys are the ids of conversations and whose values are the
                corresponding Conversation
        """
        url = self.base_api_url + f'/conversations'
        params = {
            'filter': [],
            'scope': scope,
            'per_page': count
        }
        conversation_list = []

        if parent != None:
            if parent.type == 'Course':
                params['filter'] += [f'course_{parent.id}']
            if parent.type == 'User':
                params['filter'] += [f'user_{parent.id}']
        if params['filter'] == []:
            params['filter'] = None

        if filter != None:
            params['filter'] = filter

        if count == 0:
            params['per_page'] = 100
            for scope_type in scope:
                if scope_type == 'read_and_unread':
                    conversation_list += GET_list(self.session, self.auth, url, params = params)
                elif scope_type in ['unread', 'starred', 'archived', 'sent']:
                    conversation_list += GET_list(self.session, self.auth, url, params = params | {'scope': scope_type})
        else:
            for scope_type in scope:
                if scope_type == 'read_and_unread':
                    response = self.session.get(url, headers = self.auth, params = params)
                    conversation_list += response.json()
                elif scope_type in ['unread', 'starred', 'archived', 'sent']:
                    response = self.session.get(url, headers = self.auth, params = params | {'scope': scope_type})
                    conversation_list += response.json()
        if parent == None:
            parent = self
        return list_to_dict(parent, Conversation, conversation_list)

    def get_course(self, course_id: int, json_dict: dict = None) -> Course:
        """
        Creates a Course CanvasObject from either a json dictionary or from an API call. If given a json dictionary,
        the course_id is ignored.
        
        Endpoint (when used):
            v1/courses/{course_id}

        Args:
            json_dict (dict): A dictionary obtained from an API call representing the contents of a dictionary.
            course_id (int): The course ID of the course.

        Returns:
            Course: The Course contained in the json_dict or with the given course_id.
        """
        if json_dict == None:
            url = self.base_api_url + f'/courses/{course_id}'
            return Course(self, self.session.get(url, headers = self.auth).json())
        else:
            return Course(self, json_dict)

    def get_courses(self) -> dict[Course]:
        """
        Get all courses associated with the active user.
        
        Endpoint:
            v1/courses

        Args:
            TODO: Add enrollment types

        Returns:
            dict[Courses]: A dictionary whose keys are the ids of courses and whose values are the
                corresponding Course
        """
        url = self.base_api_url + '/courses?per_page=100'
        course_list = GET_list(self.session, self.auth, url)
        return list_to_dict(self, Course, course_list)
    
    def set_tz(self, tz: str) -> None:
        """
        Sets the timezone for the Canvas object
        
        Args:
            tz (str): pytz timezone string
        
        returns:
            None
        """
        from pytz import timezone
        self.tz = timezone(tz)