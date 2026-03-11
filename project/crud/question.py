from sqlalchemy.orm import Session
from models import Question


# ── CREATE ──────────────────────────────────────────────────────────────────

def create_question(
    db: Session,
    title: str,
    code: str,
    category_id: int | None = None,
) -> Question:
    question = Question(title=title, code=code, category_id=category_id)
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


# ── READ ─────────────────────────────────────────────────────────────────────

def get_question(db: Session, question_id: int) -> Question | None:
    return db.query(Question).filter(Question.id == question_id).first()


def get_all_questions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Question]:
    return db.query(Question).offset(skip).limit(limit).all()


def get_questions_by_category(
    db: Session,
    category_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Question]:
    return (
        db.query(Question)
        .filter(Question.category_id == category_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def search_questions_by_title(
    db: Session,
    keyword: str,
    skip: int = 0,
    limit: int = 100,
) -> list[Question]:
    return (
        db.query(Question)
        .filter(Question.title.ilike(f"%{keyword}%"))
        .offset(skip)
        .limit(limit)
        .all()
    )


# ── UPDATE ───────────────────────────────────────────────────────────────────

def update_question(
    db: Session,
    question_id: int,
    title: str | None = None,
    code: str | None = None,
    category_id: int | None = None,
) -> Question | None:
    question = get_question(db, question_id)
    if question is None:
        return None

    if title is not None:
        question.title = title
    if code is not None:
        question.code = code
    if category_id is not None:
        question.category_id = category_id

    db.commit()
    db.refresh(question)
    return question


# ── DELETE ───────────────────────────────────────────────────────────────────

def delete_question(db: Session, question_id: int) -> bool:
    question = get_question(db, question_id)
    if question is None:
        return False

    db.delete(question)
    db.commit()
    return True
