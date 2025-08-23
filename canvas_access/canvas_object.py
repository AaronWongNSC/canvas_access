"""
Module for the core CanvasObject functionality. 
"""

from datetime import datetime
from typing import Self 
from canvas_access.util import z_time_str_test, z_time_str_to_dt, dt_to_local_str

class CanvasObject:
    """
    A generic object for canvas_access.

    Attributes:
        id (int): All Canvas objects have an ID.
        info_keys (list[str]): The list of keys to display when using .info().
        lineage (list[dict]]): This keeps track of the where the current object came from. This is used for the logic of
            certain methods and functions. Each dict contains some minimal information such as id and type.
        type (str): Describes the content of the objects.
        - Additional attributes will be generated from the API call
    
    Methods:
        all_info(): Displays all of the attributes of the CanvasObject
        info(): Displays only the attributes listed in info_keys
        inherit(): Passes data from the parent CanvasObject to the child (self) CanvasObject
    """

    def __init__(self, json_dict: dict):
        if 'id' not in self.__dict__.keys():
            self.id = None
        if 'info_keys' not in self.__dict__.keys():
            self.info_keys = []
        if 'lineage' not in self.__dict__.keys():
            self.lineage = None
        if 'type' not in self.__dict__.keys():
            self.type = 'CanvasObject'
        
        for key, item in json_dict.items():
            self.__dict__[key] = item

            # For time objects, create both a UTC datetime object and local time string
            # The _display object is a string that shows time in the "most convenient" manner (either local time or Z-time) 
            if z_time_str_test(item):
                self.__dict__[key + '_dt'] = z_time_str_to_dt(item)
                self.__dict__[key + '_display'] = z_time_str_to_dt(item)
                if 'tz' in self.__dict__:
                    if self.tz != None:
                        self.__dict__[key + '_localtime'] = dt_to_local_str(self.__dict__[key + '_dt'], self.tz)
                        self.__dict__[key + '_display'] = dt_to_local_str(self.__dict__[key + '_dt'], self.tz)

    def all_info(self) -> None:
        """Displays all attributes"""
        print(f'{self.type} all info:')
        for key in sorted(self.__dict__.keys()):
            print(f'\t{key}:\t{self.__dict__[key]}')
            
    def info(self) -> None:
        """Displays the attributes in info_keys"""
        print(f'{self.type} info:')
        for key in ['id'] + self.info_keys:
            if key in self.__dict__.keys():
                print(f'\t {key}:\t{self.__dict__[key]}')
    
    def inherit(self, parent: Self, additional: list[str] = []) -> None:
        """
        Pass information from parent CanvasObject to child (self) CanvasObject. The copy
        module is important because each object needs its own copy to avoid creating weirdness
        in references.
        
        Arguments:
            Parent (CanvasObject): The CanvasObject that created the chile (self) CanvasObject
            additional (list[str]): Additional keys to inherit from the parent
        """
        from copy import copy
        for key in ['session', 'auth', 'tz', 'base_api_url'] + additional:
            if key in parent.__dict__.keys():
                self.__dict__[key] = parent.__dict__[key]
        self.lineage = copy(parent.lineage) + [{
            'id': parent.id,
            'type': parent.type
            }]