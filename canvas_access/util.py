"""
Module that contains useful functions used throughout the canvas_access module

Functions:
    clean_html(): Converts an HTML string to plain text
    dt_to_local_str(): Convert a Z-time datetime object into a local time string
    GET_list(): GET data using an API call, working through the pagination
    list_to_dict(): Converts a list from the API into a dictionary
    parse_nagivation_links(): Gets the navigation links from the header of the API response
    print_dict(): Prints the CanvasObjects in a dictionary (sorted by id or by the order sent by the API)
    z_time_str_test(): Determines if a string is a Z-time. [There is probably a better way to do this?]
    z_time_str_to_dt(): Convert a Z-time string to a datetime object
"""

from datetime import datetime 
from typing import TypeVar, Type

T = TypeVar('T')

def clean_html(html_string: str) -> str:
    """
    Converts HTML to plain text.
    
    Args:
        html_string (str): The string containing HTML to be converted
    
    Returns:
        string: The plain text version of the HTML content.
    """
    if html_string == None:
        return None

    import re

    def strip_html_regex(html_string):
        clean = re.compile('<.*?>')
        return re.sub(clean, '', html_string)
    
    html_string = html_string.replace('<br>', 'NEWLINE')
    html_string = html_string.replace('</p>', 'NEWLINE</p>')
    html_string = html_string.replace('<img', ' IMAGE <img')

    plain_text = strip_html_regex(html_string)
    plain_text = plain_text.replace('NEWLINE', '\n')

    return plain_text

def dt_to_local_str(dt: datetime, tz = 'pytz.timezone') -> str:
    """
    Convert a datetime object into a local time string.
    
    Args:
        dt (datetime): The datetime object being converted to a string.
        tz (pytz.timezone): The local timezone. This is typically the tz attribute
            of the object. This is set at the Canvas CanvasObject level. 
    
    Returns:
        str: The local time string of the original datetime object.
    """
    return dt.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")

def GET_list(session: 'requests.session.Session', headers: dict, first_url: str, params: dict = {} ) -> list[dict]: # type: ignore
    """
    Gets all the data from the API call, working through all the pagination
    
    Args:
        session (requests.session.Session): The session used for the API call.
        headers (dict): Typically contains just API_KEY.
        first_url (str): URL for the first page of the contents. This is typically the API endpoint.
        params (dict): Any parameters that will be sent with the request.
    """
    this_list = []
    url = first_url
    while True:
        response = session.get(url, headers = headers, params = params)
        this_list += response.json()

        if 'link' in response.headers.keys():
            first_link, current_link, next_link, last_link = parse_navigation_links(response.headers['link'].split(','))

            if current_link == last_link:
                break
            url = next_link
        else:
            break
    return this_list

def list_to_dict(parentCanvasObject: 'CanvasObject', Class: Type[T], object_list: list[dict]) -> dict['CanvasObject']: # type: ignore
    """
    Converts a list of dictionary objects from the API into a dictionary of CanvasObjects.
    
    Args:
        ParentCanvasObject[CanvasObject]: The CanvasObject that is making the API call. This
            will be important for inheritance.
        Class (CanvasObject class): The output CanvasObject class.
        object_list (list[dict]): A list of dictionaries from the API that represents the data
            that needs to be converted into CanvasObjects.
    """
    canvasObject_dict = {}
    for object in object_list:
        canvasObject_dict[object['id']] = Class(parentCanvasObject, object)
    return canvasObject_dict

def parse_navigation_links(link_list: list[str]) -> tuple[str, str, str, str]:
    """
    Parses the json header to get the navigation links
    
    Args:
        link_list (list[str]): The data from the 'link' key in the header from the API.

    Returns:
        tuple[str, str, str, str]: Four URLs corresponding to the four keys.
            - first, current, next, last

    """
    first_link = ''
    current_link = ''
    next_link = ''
    last_link = ''
    for link_info in link_list:
        if 'rel="first"' in link_info:
            first_link = link_info.split(';')[0].strip('<>')
        if 'rel="current"' in link_info:
            current_link = link_info.split(';')[0].strip('<>')
        if 'rel="next"' in link_info:
            next_link = link_info.split(';')[0].strip('<>')
        if 'rel="last"' in link_info:
            last_link = link_info.split(';')[0].strip('<>')
    return first_link, current_link, next_link, last_link

def print_dict(canvasObject_dict: dict['CanvasObject'], sort: str = 'id_desc') -> None: # type: ignore
    """
    Print the CanvasObjects in a dictionary.
    
    Args:
        canvasObject_dict (dict[CanvasObject]): Dictionary of CanvasObjects, typically
            obtained from a get_Class() method.
        sort (str): Sort method. The default is to print in decreasing order by id, which
            normally causes the newest objects to be on top.
            -- 'id_asc': Sort ascending by CanvasObject ID.
            -- 'natural': Use the natural order provided by the dictionary
            -- TODO: 'custom_<name>': Custom ordering using the CanvasObject attribute <name>
            -- Any other string will result in the default sort.
    
    Returns:
        None
    """
    if sort == 'id_asc':
        print_order = sorted(canvasObject_dict.keys(), reverse = False)
    elif sort == 'natural':
        print_order = canvasObject_dict.keys()
    elif sort[:7] == 'custom_':
        sort_attribute = sort[7:]
        attribute_found = 0
        for object_id, object in canvasObject_dict.items():
            if sort_attribute in object.__dict__.keys():
                attribute_found += 1
        if attribute_found == len(canvasObject_dict):
            print_order = sorted(canvasObject_dict.items(), key=lambda item: item[1].__dict__[sort_attribute])
        else:
            print_order = sorted(canvasObject_dict.keys(), reverse = True)
    else:
        print_order = sorted(canvasObject_dict.keys(), reverse = True)

    for object_id in print_order:
        print(canvasObject_dict[object_id])

def z_time_str_test(test_str: str) -> bool:
    """
    Determine if a string is a Z-time string.

    Args:
        test_str (str): The string to be tested as a z-time string.
            - Z-time format: YYYY-MM-DDTHH:MM:SSZ
            - ISO format of z-time: YYYY-MM-DDTHH:MM:SS+00:00

    Returns:
        bool:
            - True if datetime object is successfully created
            - False if datetime object is not successfully created
    """
    try:
        datetime.fromisoformat(test_str.replace('Z', '+00:00'))
        return True
    
    except:
        return False

def z_time_str_to_dt(z_time_str: str) -> datetime:
    """
    Convert a Z-time string to a datetime object.
    
    Args:
        z_time_str: A Z-time string. Note that this does not error-check, so 
            z_time_str_test() should be run on the string before this happens.
    
    Returns:
        datetime: A datetime object matching the Z-time.
    """
    return datetime.fromisoformat(z_time_str.replace('Z', '+00:00'))