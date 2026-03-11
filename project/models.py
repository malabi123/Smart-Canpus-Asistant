from sqlalchemy import (
    Column, String, Integer, Text, DateTime, ForeignKey, CheckConstraint, Boolean, UniqueConstraint
)
from sqlalchemy.orm import relationship
from db import Base


class Lecturer(Base):
    __tablename__ = 'lecturers'

    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)

    courses = relationship('Course', back_populates='lecturer')

    __table_args__ = (
        CheckConstraint(
            "name ~ '^[A-Za-z]{2,}(?:[ ''-][A-Za-z]{2,})+$'",
            name="ck_lecturer_name_min2words_min2letters"),
    )

    def __str__(self):
        return f"Lecturer(id:{self.id}, name:'{self.name}')"


class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    building = Column(Integer, nullable=False)
    number = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)

    lessons = relationship('Lesson', back_populates='room')

    __table_args__ = (
        CheckConstraint(
            "capacity >= 0", name='chk_room_capacity_min_0'),
        CheckConstraint(
            "capacity >= 0", name='chk_room_building_min_0'),
        UniqueConstraint('building', 'number', name='uq_number_per_building'),
    )

    def __str__(self):
        return f"Room(id:{self.id}, building:{self.building}, number:{self.number}, capacity:{self.capacity})"


class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    lecturer_id = Column(Integer, ForeignKey('lecturers.id'))
    year = Column(Integer, nullable=False)
    semester = Column(String(1))

    lecturer = relationship('Lecturer', back_populates='courses')
    lessons = relationship('Lesson', back_populates='course')

    def __str__(self):
        return f"Course(id:{self.id}, name:'{self.name}', year:{self.year}, semester:'{self.semester}')"


class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    room_id = Column(Integer, ForeignKey('rooms.id'))
    date = Column(DateTime, nullable=False)
    is_test = Column(Boolean, default=False)

    course = relationship('Course', back_populates='lessons')
    room = relationship('Room', back_populates='lessons')

    __table_args__ = (
        UniqueConstraint('room_id', 'date', name='uq_room_per_date'),
    )

    def __str__(self):
        return f"Lesson(id:{self.id}, course_id:{self.course_id}, room_id:{self.room_id}, date:{self.date}, is_test:{self.is_test})"


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True)

    questions = relationship('Question', back_populates='category')

    def __str__(self):
        return f"{self.id} - {self.name}"


class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    title = Column(String(50), nullable=False)
    code = Column(Text, nullable=False)

    category = relationship('Category', back_populates='questions')
