from datetime import datetime 
from canvas_access.util import z_time_str_test, z_time_str_to_dt, z_time_dt_to_local_str

class CanvasObject:
    def __init__(self, json_dict):
        self.__dict__['id'] = None
        
        for key, item in json_dict.items():
            self.__dict__[key] = item
            if z_time_str_test(item):
                self.__dict__[key + '_dt'] = z_time_str_to_dt(item)
                if 'tz' in self.__dict__:
                    if self.tz != None:
                        self.__dict__[key + '_localtime'] = z_time_dt_to_local_str(self.__dict__[key + '_dt'], self.tz)

    def all_info(self):
        print(f'{self.type} all info:')
        for key in sorted(self.__dict__.keys()):
            print(f'\t{key}:\t{self.__dict__[key]}')
        return
            
    def info(self):
        print(f'{self.type} info:')
        for key in ['id'] + self.info_keys:
            if key in self.__dict__.keys():
                print(f'\t {key}:\t{self.__dict__[key]}')
        return
    
    def inherit(self, Parent, additional = []):
        for key in ['session', 'auth', 'tz', 'base_api_url'] + additional:
            if key in Parent.__dict__.keys():
                self.__dict__[key] = Parent.__dict__[key]
        return

