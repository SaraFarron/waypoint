import random

from sqlmodel import Session

from app.models import Expence, TransactionCreate
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_expence(db: Session) -> Expence:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    category = random_lower_string()
    amount = round(random.uniform(1, 1000), 2)
    expence_in = TransactionCreate(title=title, category=category, amount=amount)
    expence = Expence.model_validate(expence_in, update={"owner_id": owner_id})
    db.add(expence)
    db.commit()
    db.refresh(expence)
    return expence
