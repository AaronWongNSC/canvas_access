"""
Module for the Conversation CanvasObject for the canvas_access module. 
"""

from canvas_access.canvas_object import CanvasObject
from canvas_access.message import Message
from canvas_access.util import GET_list, list_to_dict

class Conversation(CanvasObject):
    """
    Conversation CanvasObject for canvas_access.

    Attributes:
        Universal attributes: auth, base_api_url, session, tz
        General attributes: info_keys, lineage, type
        Other inherited attributes: Varies with parent
            User: user_id, user_name
            Course: course_id, course_name
        Converation-level attributes:
            last_activity (str): Text display of the last activity in the Conversation.
            participant_list (list[str]): A list of the names of the participating students.
            - Others obtained from API
    
    Methods:
        get_messages(): Get the Messages in the Conversation
        TODO: get_course_context(): Get the course information connected to the conversation
        TODO: get_participants(): Get all the participants in the conversation as User CanvasObjects
    """

    def __init__(self, parent, json_dict):
        self.inherit(parent)
        if parent.type == 'User':
            self.user_id = parent.id
            self.user_name = parent.name
            for key in ['course_id', 'course_name']:
                if key in parent.__dict__.keys():
                    self.__dict__[key] = parent.__dict__[key]
        elif parent.type == 'Course':
            self.course_id = parent.id
            self.course_name = parent.name

        super().__init__(json_dict)

        self.info_keys = ['context_code', 'context_name', 'participant_list', 'subject', 'message_count']
        self.type = 'Conversation'
        self.participant_list = [ participant['name'] for participant in self.participants ]

        activity = []
        if self.last_authored_message_at != None:
            activity.append(self.last_authored_message_at_display)
        if self.last_message_at != None:
            activity.append(self.last_message_at_display)
        if len(activity) == 0:
            self.last_activity = None
        else:
            self.last_activity = max(activity)

    def __str__(self):
        return f'{self.type} (Parent: {self.lineage[-1]['type']}): {self.id} \t{self.last_activity} \t{self.subject} \t{self.participant_list}'

    def get_messages(self) -> dict[Message]:
        """
        Get all of the messages in the conversation
        
        Endpoint:
            v1/conversations/{conversation_id}

        Args:
            None

        Returns:
            dict[Message]: The Messages in the conversation
        """
        url = self.base_api_url + f'/conversations/{self.id}'
        response = self.session.get(url, headers = self.auth)
        return list_to_dict(self, Message, response.json()['messages'])

def start_conversation(canvas: 'Canvas', recipients: list['User'], subject: str, body: str, group_conversation: bool = False) -> dict[Conversation]: # type: ignore
    """
    Start a new conversation
    
    Endpoint:
        v1/conversations/

    Args:
        session (Canvas): A Canvas CanvasObject
        recipients (list[User]): Recipients of the message as either a single user or a list of Users.
        subject (str): Subject of the conversation.
        body (str): Body of the initial message.
        force_new (bool): Forces the conversation to be new by default.

    Returns:
        None (Though I should probably make it return list[Conversation] at some point... there are inheritance issues)
    """
    if type(recipients) == 'canvas_access.user.User':
        recipients = [recipients]
    
    first_user = recipients[0]

    # Determine context code
    context_codes = []
    for user in recipients:
        if user.lineage[-1]['type'] == 'Course':
            context_codes.append(f'course_{user.course_id}')
        else:
            context_codes.append(f'None')
    if len(set(context_codes)) == 1:
        context_code = context_codes[0]
    else:
        context_code = ''

    url = canvas.base_api_url + '/conversations'
    params = {
        'recipients[]': [recipient.id for recipient in recipients],
        'group_conversation': group_conversation,
        'subject': subject,
        'body': body,
        'context_code': context_code
    }
    response = canvas.session.post(url, headers = canvas.auth, params = params)
    if '201' in response.headers['status']:
        print('Message sent!')
        if 'course' in context_code:
            parent = canvas.get_course(int(context_code.strip('course_')))
        else:
            parent = canvas
        conversations = []
        for conversation_dict in response.json():
            conversations.append(Conversation(parent, conversation_dict))
    else:
        print('Message failed!')
        conversations = []
    return {conversation.id: conversation for conversation in conversations}