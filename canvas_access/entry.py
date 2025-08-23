"""
Module for the Entry CanvasObject for the canvas_access module. 
"""

from canvas_access.canvas_object import CanvasObject
from canvas_access.util import clean_html, GET_list, list_to_dict

class Entry(CanvasObject):
    """
    Entry CanvasObject for canvas_access.

    Attributes:
        Universal attributes: auth, base_api_url, session, tz
        General attributes: info_keys, lineage, type
        Other inherited attributes: course_id, course_name, discussion_id, discussion_title
        Course-level attributes:
            message_text (str): A plain text version of the message.
            user_name (str): Display name of the user
            - Others obtained from API
    
    Methods:
        None
    """
    def __init__(self, discussion, json_dict):
        self.inherit(discussion, ['course_id', 'course_name'])
        self.discussion_id = discussion.id
        self.discussion_title = discussion.title

        self.info_keys = ['course_id', 'course_name', 'discussion_id', 'id', 'user_name']
        self.type = 'Entry'
        self.reply_list = []

        super().__init__(json_dict)

        if 'deleted' in self.__dict__.keys():
            if self.deleted == True:
                self.message = 'DELETED MESSAGE'
                self.user_id = self.editor_id
        self.message_text = clean_html(self.message)

    def __str__(self):
        return f'{self.type} [Course ID: {self.course_id}]: {self.id} \tAuthor: {self.user_name} \tReply to: {self.parent_id} \tReplies: {self.reply_list}'