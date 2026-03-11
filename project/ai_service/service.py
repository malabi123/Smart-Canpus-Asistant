import os
from pathlib import Path
from dotenv import load_dotenv
import openai

from .prompt import PROMPT_TEMPLATE
from .utility import parse_response, get_Categories, DEFAULT_CATEGORIES_LIST


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


base_path = Path(__file__).resolve().parent
file_path = base_path / "model.txt"

try:
    code_content = file_path.read_text(encoding="utf-8")
except FileNotFoundError:
    print("model.txt not found")
    raise


def build_prompt(user_question: str, code_content: str, session) -> str:
    return PROMPT_TEMPLATE \
        .replace("<CODE_CONTENT>", code_content) \
        .replace("<CATEGORIES_LIST>", get_Categories(session) or DEFAULT_CATEGORIES_LIST) \
        .replace("<USER_QUESTION>", user_question)


def send_request(user_question: str, session) -> dict:
    prompt = build_prompt(user_question, code_content, session)
    try:
        response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        raw_text = response.choices[0].message.content.strip()

        return parse_response(raw_text)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
