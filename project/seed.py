from datetime import datetime
from models import Lecturer, Room, Course, Lesson, Category
from db import get_session, Base, engine


def seed():
    Base.metadata.create_all(engine)
    with get_session() as db:

        # ── Lecturers ─────────────────────────────────────────────────────────────
        daniel = Lecturer(name="Daniel Cohen")
        sarah = Lecturer(name="Sarah Miller")
        db.add_all([daniel, sarah])
        db.flush()

        # ── Rooms (all in building 1) ─────────────────────────────────────────────
        room_01 = Room(building=1, number=1,   capacity=30)
        room_02 = Room(building=1, number=2,   capacity=50)
        room_101 = Room(building=1, number=101, capacity=120)
        db.add_all([room_01, room_02, room_101])
        db.flush()

        # ── Courses (year 2026, semester B) ───────────────────────────────────────
        algorithms = Course(name="Introduction to Algorithms",
                            lecturer_id=daniel.id, year=2026, semester="B")
        os_course = Course(name="Operating Systems",
                           lecturer_id=sarah.id,  year=2026, semester="B")
        databases = Course(name="Database Systems",
                           lecturer_id=daniel.id, year=2026, semester="B")
        db.add_all([algorithms, os_course, databases])
        db.flush()

        # ── Lessons ───────────────────────────────────────────────────────────────
        #
        # Course 1 – "Introduction to Algorithms"  (Daniel, room_01)
        #   Regular slot : Sundays  12:00
        #   Early lesson  : week 3, Apr 19 at 10:00  (2 hours earlier)
        #   Last lesson   : week 8, is_test = True
        #
        # Course 2 – "Operating Systems"           (Sarah, room_02)
        #   Regular slot : Mondays  10:00
        #   Early lesson  : week 5, May 4  at 08:00  (2 hours earlier)
        #   Last lesson   : week 8, is_test = True
        #
        # Course 3 – "Database Systems"            (Daniel, room_101)
        #   Regular slot : Tuesdays 14:00
        #   Early lesson  : week 4, Apr 28 at 12:00  (2 hours earlier)
        #   Last lesson   : week 8, is_test = True
        #
        # Constraint checks:
        #   • Each course uses a different room  → no (room, date) collision
        #   • Daniel teaches Sun + Tue           → no lecturer time overlap
        #   • Sarah teaches Mon only             → no lecturer time overlap

        course1_slots = [
            (datetime(2026, 4,  5, 12, 0), False),  # week 1 – Sun Apr  5
            (datetime(2026, 4, 12, 12, 0), False),  # week 2 – Sun Apr 12
            # week 3 – Sun Apr 19  <- EARLY (10:00)
            (datetime(2026, 4, 19, 10, 0), False),
            (datetime(2026, 4, 26, 12, 0), False),  # week 4 – Sun Apr 26
            (datetime(2026, 5,  3, 12, 0), False),  # week 5 – Sun May  3
            (datetime(2026, 5, 10, 12, 0), False),  # week 6 – Sun May 10
            (datetime(2026, 5, 17, 12, 0), False),  # week 7 – Sun May 17
            # week 8 – Sun May 24  <- TEST
            (datetime(2026, 5, 24, 12, 0), True),
        ]

        course2_slots = [
            (datetime(2026, 4,  6, 10, 0), False),  # week 1 – Mon Apr  6
            (datetime(2026, 4, 13, 10, 0), False),  # week 2 – Mon Apr 13
            (datetime(2026, 4, 20, 10, 0), False),  # week 3 – Mon Apr 20
            (datetime(2026, 4, 27, 10, 0), False),  # week 4 – Mon Apr 27
            # week 5 – Mon May  4  <- EARLY (08:00)
            (datetime(2026, 5,  4,  8, 0), False),
            (datetime(2026, 5, 11, 10, 0), False),  # week 6 – Mon May 11
            (datetime(2026, 5, 18, 10, 0), False),  # week 7 – Mon May 18
            # week 8 – Mon May 25  <- TEST
            (datetime(2026, 5, 25, 10, 0), True),
        ]

        course3_slots = [
            (datetime(2026, 4,  7, 14, 0), False),  # week 1 – Tue Apr  7
            (datetime(2026, 4, 14, 14, 0), False),  # week 2 – Tue Apr 14
            (datetime(2026, 4, 21, 14, 0), False),  # week 3 – Tue Apr 21
            # week 4 – Tue Apr 28  <- EARLY (12:00)
            (datetime(2026, 4, 28, 12, 0), False),
            (datetime(2026, 5,  5, 14, 0), False),  # week 5 – Tue May  5
            (datetime(2026, 5, 12, 14, 0), False),  # week 6 – Tue May 12
            (datetime(2026, 5, 19, 14, 0), False),  # week 7 – Tue May 19
            # week 8 – Tue May 26  <- TEST
            (datetime(2026, 5, 26, 14, 0), True),
        ]

        lessons = (
            [Lesson(course_id=algorithms.id, room_id=room_01.id,
                    date=dt, is_test=t) for dt, t in course1_slots]
            + [Lesson(course_id=os_course.id,  room_id=room_02.id,
                      date=dt, is_test=t) for dt, t in course2_slots]
            + [Lesson(course_id=databases.id,  room_id=room_101.id,
                      date=dt, is_test=t) for dt, t in course3_slots]
        )
        db.add_all(lessons)
        db.flush()

        categories = [
            Category(name="Schedule"),
            Category(name="General Information"),
            Category(name="Technical Issue"),
        ]

        db.add_all(categories)

        db.commit()
        print("Seed data inserted successfully.")


if __name__ == "__main__":
    seed()
