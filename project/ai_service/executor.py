from models import Lesson, Lecturer, Room, Course
from db import get_session
from .service import send_request
from .utility import get_category_name


def execute(q: str) -> dict:
    with get_session() as session:
        result = send_request(q, session)
        if 'error' in result:
            return f'Something went wrong,Could not do {q}'

        local_vars = {
            "session": session,
            "Lesson": Lesson,
            "Lecturer": Lecturer,
            "Room": Room,
            "Course": Course
        }
        try:
            code = result.get('code', "")
            print(code)
            if code:
                exec(code, {"__builtins__": __builtins__}, local_vars)
            s = str(local_vars.get(
                "s", "Something went wrong, ai response went wrong"))
            result['cat_id'] = result['category']
        except Exception as e:
            s = 'something went wrong, could not do ai code'
            result['cat_id'] = '0'

        if result['category'] == 0:
            result['category'] = 'error'
        else:
            result['category'] = get_category_name(session, result["category"])
        result['answer'] = s
    return result
