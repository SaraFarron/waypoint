import random

from sqlmodel import Session

from app.models import Income, TransactionCreate
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_income(db: Session) -> Income:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    category = random_lower_string()
    amount = round(random.uniform(1, 1000), 2)
    income_in = TransactionCreate(title=title, category=category, amount=amount)
    income = Income.model_validate(income_in, update={"owner_id": owner_id})
    db.add(income)
    db.commit()
    db.refresh(income)
    return income
