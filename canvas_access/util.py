from datetime import datetime 
import pytz
tz = pytz.timezone('America/Los_Angeles')

def GET_list(session, headers, first_url, params = {} ):
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

def list_to_dict(ParentCanvasObject, Class, object_list):
    CanvasObject_dict = {}
    for object in object_list:
        CanvasObject_dict[object['id']] = Class(ParentCanvasObject, object)
    return CanvasObject_dict

def print_dict(CanvasObject_dict):
    for object_id, object in CanvasObject_dict.items():
        print(object)
    return

def parse_navigation_links(link_list):
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

def z_time_str_test(z_time_str):
    try:
        datetime.fromisoformat(z_time_str.replace('Z', '+00:00'))
        return True
    
    except:
        return False

def z_time_str_to_dt(z_time_str):
    return datetime.fromisoformat(z_time_str.replace('Z', '+00:00'))

def z_time_dt_to_local_str(z_time_dt, tz):
    return z_time_dt.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")