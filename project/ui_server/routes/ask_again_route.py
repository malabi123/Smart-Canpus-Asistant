from fastapi import APIRouter, Request, Header, HTTPException
from question_service.service import get_task, get_titles as fetch_titles

router = APIRouter(prefix='/again')


@router.get('/questions/{q_id}')
def get_answer(
        q_id: str):
    return get_task(q_id.strip())


@router.get('/titles')
def get_titles():
    return fetch_titles()
