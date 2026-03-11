import json
import re
from sqlalchemy.orm import Session

from models import Category

DEFAULT_CATEGORIES_LIST = "1 - Schedule, 2 - General Information, 3 - Technical Issue"


def parse_response(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            raw = re.sub(r'```[a-z]*\n?', '', raw).strip()
            raw = raw.replace('```', '').strip()
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                raw = match.group(0)
            # fix real newlines AND control characters inside the "code" field

            def fix_code_field(m):
                code_value = m.group(1)
                code_value = code_value.replace('\n', '\\n')
                code_value = code_value.replace('\r', '\\r')
                code_value = code_value.replace('\t', '\\t')
                return f'"code":"{code_value}"'
            raw = re.sub(
                r'"code":"(.*?)"(?=\s*[,}])', fix_code_field, raw, flags=re.DOTALL)
            return json.loads(raw)
        except json.JSONDecodeError as e:
            return {"error": f"Response is not valid JSON: {str(e)}", "raw": raw}


def get_Categories(session: Session) -> str | None:
    categories = session.query(Category).all()
    if not categories:
        return None
    return ','.join([str(c) for c in categories])


def get_category_name(session: Session, id):
    category = session.query(Category).where(Category.id == id).first()
    if not category:
        return None
    return category.name
