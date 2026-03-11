
from db import get_session
from crud.question import create_question, get_question, get_all_questions
from models import Question, Category
from .executor import execute


def save_question(d: dict):
    try:
        with get_session() as session:
            q = create_question(
                session, d['title'], d['code'].replace('\\', '\\\\'), d['cat_id'])
            if not q:
                return False
            return True
    except Exception as e:
        print(e)
        return False


def get_task(q_id: str):
    try:
        n = int(q_id)
    except:
        return {"error": "invalid input"}
    with get_session() as session:
        q = get_question(session, q_id)
        if not q:
            return {'title': 'error',
                    'category': 'error',
                    'answer': 'question not found'}
        title = q.title
        category = q.category
        category = category.name if category else 'general'
        success, answer = execute(session, q.code)
        return {
            'title': title if success else 'error',
            'category': category if success else 'error',
            'answer': answer
        }


def get_titles():
    with get_session() as session:
        q_list = get_all_questions(session)
        return {str(q.id): q.title for q in q_list}
