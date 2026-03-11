from models import Lesson, Lecturer, Room, Course


def execute(session, code: str):
    success = False
    local_vars = {
        "session": session,
        "Lesson": Lesson,
        "Lecturer": Lecturer,
        "Room": Room,
        "Course": Course,
    }
    try:
        code = code.replace('\\\\', '\\')
        exec(code, {"__builtins__": __builtins__}, local_vars)
        s = str(local_vars.get(
            "s", "Something went wrong, ai response went wrong"))
        if 's' in local_vars:
            success = True
    except Exception as e:
        s = "Something went wrong, ai response went wrong"
    return success, s
