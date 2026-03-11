from fastapi import APIRouter, Request, Header, HTTPException
import threading
import uuid
from pydantic import BaseModel

from ui_server.utility import set_fall_back
from question_service.service import save_question
from ai_service.executor import execute
from .ask_again_route import router as again_router

router = APIRouter(prefix='/ask')
tasks = {}

router.include_router(again_router)


class Question(BaseModel):
    question: str


@router.post('/')
async def ask(
    question: Question,
    request: Request,
    user_token: str = Header(...)
):
    if (question.question.strip() == ""):
        return
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "user_token": user_token,
        "question": question.question,
        "status": "processing",
        "times": 0,
        'save': 0
    }

    def ask_question():
        result = execute(question.question)
        task = tasks[task_id]
        task['answer'] = result['answer']
        task['title'] = result['title']
        task['category'] = result['category']
        task['cat_id'] = result['cat_id']
        task['save'] = 1 if result['cat_id'] not in (0, '0') else 0
        task['status'] = 'done'
        task['code'] = result['code']

    threading.Thread(target=ask_question).start()
    return {'task_id': task_id}


@router.get('/{task_id}')
def get_answer(
        task_id: str,
        user_token: str = Header(...)):
    task = tasks.get(task_id)
    if not task or user_token != task['user_token']:
        raise HTTPException(
            status_code=404, detail="Task not found or unauthorized")
    if task['status'] == 'processing':
        task['times'] = task['times'] + 1
        if task['times'] == 10:
            set_fall_back(task)

    return {
        'status': task['status'],
        'title': task.get('title'),
        'category': task.get('category'),
        'answer': task.get('answer'),
        'save': task['save']
    }


@router.post('/{task_id}/save')
def save_answer(
        task_id: str,
        user_token: str = Header(...)):
    task = tasks.get(task_id)
    if not task or user_token != task['user_token']:
        raise HTTPException(
            status_code=404, detail="Task not found or unauthorized")
    if task['status'] != 'done' or task['save'] == '0' or not save_question(task):
        return {
            'status': 'unable to save this question '
        }
    return {
        'status': 'saved successfully'
    }
