"""
Module for the Message CanvasObject for the canvas_access module. 
"""

from canvas_access.canvas_object import CanvasObject
from canvas_access.util import GET_list, list_to_dict

class Message(CanvasObject):
    """
    Message CanvasObject for canvas_access.

    Attributes:
        Universal attributes: auth, base_api_url, session, tz
        General attributes: info_keys, lineage, type
        Other inherited attributes: conversation_id, conversation_subject
        Course-level attributes:
            author_name (str): The name of the author of the message.
            participating_users (list[str]): A list of the names of the participants in the conversation.
            - Others obtained from API
    
    Methods:
        reply(): Replies to message author.
        reply_all(): Replies to multiple participating users.
        TODO: get_participants()
    """
    def __init__(self, Conversation, json_dict):
        self.inherit(Conversation, ['context_id', 'context_name', 'participants'])
        self.conversation_id = Conversation.id
        self.conversation_subject = Conversation.subject

        super().__init__(json_dict)

        self.info_keys = ['context_name', 'created_at_display', 'participating_users', 'author_name', 'subject', 'body']
        self.type = 'Message'

        self.author_name = [self.participants[count]['name']
                            for count in range(len(self.participants))
                            if self.participants[count]['id'] == self.author_id][0]
        self.participating_users = [self.participants[count]['name']
                                    for count in range(len(self.participants))
                                    if self.participants[count]['id'] in self.participating_user_ids ]
    
    def __str__(self):
        return f'{self.type} [From: {self.author_id}, Subject: {self.subject}]: {self.id} \t {self.body[:100].replace('\n', '  ')}'
    
    def check_sent(response: 'requests.models.Response') -> bool: # type: ignore
        """Check to see if the API call was successful for sending messages."""
        if '200' in response.headers['Status']:
            print('Message sent!')
        else:
            print('Error sending message')

    def reply(self, body) -> None:
        """
        Reply to the author of the message.

        Endpoint:
            v1/conversations/{conversation_id}/add_message

        Args:
            body: Text of message. Must be plain text.

        Returns:
            dict[Message]: The Messages in the conversation
        """
        url = self.base_api_url + f'/conversations/{self.conversation_id}/add_message'
        params = {
            'body': body,
            'recipients': self.author_id
        }
        response = self.session.post(url, headers = self.auth, params = params)
        self.check_sent(response)

    def reply_all(self, body, recipients = None) -> None:
        """
        Reply to multiple users that are participants in the conversation.

        Endpoint:
            v1/conversations/{conversation_id}/add_message

        Args:
            body: Text of message. Must be plain text.
            recipients: List of user_ids. If none is provided, it will reply to all participants

        Returns:
            dict[Message]: The Messages in the conversation
        """
        url = self.base_api_url + f'/conversations/{self.conversation_id}/add_message'
        params = {
            'body': body,
            'recipients[]': recipients
        }
        response = self.session.post(url, headers = self.auth, params = params)
        self.check_sent(response)
