"""
Module for the Discussion CanvasObject for the canvas_access module. 
"""

from canvas_access.canvas_object import CanvasObject
from canvas_access.entry import Entry
from canvas_access.util import GET_list, list_to_dict

class Discussion(CanvasObject):
    """
    Discussion CanvasObject for canvas_access.

    Attributes:
        Universal attributes: auth, base_api_url, session, tz
        General attributes: info_keys, lineage, type
        Other inherited attributes: None
        Course-level attributes:
            reply_list (list[int]): A list of replies to the entry
            - Others obtained from API
    
    Methods:
        get_entries(): Get all assignments within the discussion
    """
    def __init__(self, course, json_dict):
        self.inherit(course)
        self.course_id = course.id
        self.course_name = course.name

        self.info_keys = ['course_id', 'course_name', 'title']
        self.type = 'Discussion'

        super().__init__(json_dict)
    
    def __str__(self):
        return f'{self.type} [Course ID: {self.course_id}]: {self.id} \t {self.title}'
    
    def get_entries(self) -> dict[Entry]:
        """
        Gets all entries from a conversation.

        Endpoint:
            v1/courses/{course_id}/discussion_topics/{discussion_id}/view
        
        Args:
            None
        
        Returns:
            dict[Entry]: A dictionary containing Entry CanvasObjects whose keys are
                entry IDs and whose values are the Entry


        NOTE: May eventually need to deal with "has_more_replies" flag?
        """
        def get_replies(entry):
            """Recursively convert replies to entries"""
            replies = []
            if 'replies' in entry.keys():
                for reply in entry['replies']:
                    replies.append(reply)
                    replies += get_replies(reply)
            return replies

        url = self.base_api_url + f'/courses/{self.course_id}/discussion_topics/{self.id}/view'
        response = self.session.get(url, headers = self.auth)

        self.participants = response.json()['participants']
        initial_entries = response.json()['view']
        replies = []
        for entry in initial_entries:
            replies += get_replies(entry)
        entry_list = initial_entries + replies

        entry_dict = list_to_dict(self, Entry, entry_list)

        for entry_id, entry in entry_dict.items():
            if 'user_id' in entry.__dict__.keys():
                entry.user_name = [participant['display_name']
                                    for participant in self.participants
                                    if participant['id'] == entry.user_id][0]
            if entry.parent_id != None:
                entry_dict[entry.parent_id].reply_list += [entry_id]
            
        
        return entry_dict
