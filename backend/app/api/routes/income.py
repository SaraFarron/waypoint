import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Income, TransactionCreate, TransactionUpdate

router = APIRouter(prefix="/income", tags=["income"])


@router.get("/", response_model=list[Income])
def read_income(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve income records.
    """

    if current_user.is_superuser:
        statement = (
            select(Income).order_by(Income.date.desc()).offset(skip).limit(limit)  # ty:ignore[unresolved-attribute]
        )
        incomes = session.exec(statement).all()
    else:
        statement = (
            select(Income)
            .where(Income.owner_id == current_user.id)
            .order_by(Income.date.desc())  # ty:ignore[unresolved-attribute]
            .offset(skip)
            .limit(limit)
        )
        incomes = session.exec(statement).all()

    return incomes


@router.get("/{id}", response_model=Income)
def read_one_income(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get income by ID.
    """
    income = session.get(Income, id)
    if not income:
        raise HTTPException(status_code=404, detail="Income not found")
    if not current_user.is_superuser and (income.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return income


@router.post("/", response_model=Income)
def create_income(
    session: SessionDep, current_user: CurrentUser, income_in: TransactionCreate
) -> Any:
    """
    Create new income.
    """
    income = Income.model_validate(income_in, update={"owner_id": current_user.id})
    income.owner_id = current_user.id
    session.add(income)
    session.commit()
    session.refresh(income)
    return income


@router.put("/{id}", response_model=Income)
def update_income(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    income_in: TransactionUpdate,
) -> Any:
    """
    Update an income.
    """
    income = session.get(Income, id)
    if not income:
        raise HTTPException(status_code=404, detail="Income not found")
    if not current_user.is_superuser and (income.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    income_data = income_in.model_dump(exclude_unset=True)
    for key, value in income_data.items():
        setattr(income, key, value)
    session.add(income)
    session.commit()
    session.refresh(income)
    return income
