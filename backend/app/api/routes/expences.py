import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Expence, ExpenceCreate, ExpenceUpdate

router = APIRouter(prefix="/expences", tags=["expences"])


@router.get("/", response_model=list[Expence])
def read_expences(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve expences.
    """

    if current_user.is_superuser:
        statement = (
            select(Expence).order_by(Expence.date.desc()).offset(skip).limit(limit)
        )
        expences = session.exec(statement).all()
    else:
        statement = (
            select(Expence)
            .where(Expence.owner_id == current_user.id)
            .order_by(Expence.date.desc())
            .offset(skip)
            .limit(limit)
        )
        expences = session.exec(statement).all()

    return expences


@router.get("/{id}", response_model=Expence)
def read_expence(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get expence by ID.
    """
    expence = session.get(Expence, id)
    if not expence:
        raise HTTPException(status_code=404, detail="Expence not found")
    if not current_user.is_superuser and (expence.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return expence


@router.post("/", response_model=Expence)
def create_expence(
    session: SessionDep, current_user: CurrentUser, expence_in: ExpenceCreate
) -> Any:
    """
    Create new expence.
    """
    expence = Expence.model_validate(expence_in, update={"owner_id": current_user.id})
    expence.owner_id = current_user.id
    session.add(expence)
    session.commit()
    session.refresh(expence)
    return expence


@router.put("/{id}", response_model=Expence)
def update_expence(
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    expence_in: ExpenceUpdate,
) -> Any:
    """
    Update an expence.
    """
    expence = session.get(Expence, id)
    if not expence:
        raise HTTPException(status_code=404, detail="Expence not found")
    if not current_user.is_superuser and (expence.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    expence_data = expence_in.model_dump(exclude_unset=True)
    for key, value in expence_data.items():
        setattr(expence, key, value)
    session.add(expence)
    session.commit()
    session.refresh(expence)
    return expence
