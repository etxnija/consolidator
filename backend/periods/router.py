"""Reporting periods API router.

Endpoints:
  POST  /periods              — create a new reporting period
  GET   /periods              — list all periods
  GET   /periods/{period_id}  — get single period
  POST  /periods/{period_id}/lock  — lock a period (prevents further ingestion)
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth.router import get_current_tenant_id
from ..database import get_db
from ..models import PeriodStatus, ReportingPeriod

router = APIRouter(prefix="/periods", tags=["periods"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class PeriodCreate(BaseModel):
    label: str = Field(..., description="Human-readable label, e.g. 'FY-2024'")
    period_start: date
    period_end: date


class PeriodResponse(BaseModel):
    period_id: uuid.UUID
    label: str
    period_start: date
    period_end: date
    status: PeriodStatus

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("", response_model=PeriodResponse, status_code=status.HTTP_201_CREATED)
def create_period(
    body: PeriodCreate,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> PeriodResponse:
    """Create a new reporting period."""
    if body.period_end < body.period_start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="period_end must be on or after period_start",
        )

    existing = (
        db.query(ReportingPeriod)
        .filter(
            ReportingPeriod.label == body.label,
            ReportingPeriod.tenant_id == tenant_id,
        )
        .one_or_none()
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A period with label {body.label!r} already exists",
        )

    period = ReportingPeriod(
        label=body.label,
        period_start=body.period_start,
        period_end=body.period_end,
        status=PeriodStatus.open,
        tenant_id=tenant_id,
    )
    db.add(period)
    db.commit()
    db.refresh(period)
    return PeriodResponse.model_validate(period)


@router.get("", response_model=List[PeriodResponse])
def list_periods(
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> List[PeriodResponse]:
    """Return all reporting periods ordered by period_end descending."""
    rows = (
        db.query(ReportingPeriod)
        .filter(ReportingPeriod.tenant_id == tenant_id)
        .order_by(ReportingPeriod.period_end.desc())
        .all()
    )
    return [PeriodResponse.model_validate(r) for r in rows]


@router.get("/{period_id}", response_model=PeriodResponse)
def get_period(
    period_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> PeriodResponse:
    """Return a single reporting period by UUID."""
    period = (
        db.query(ReportingPeriod)
        .filter(
            ReportingPeriod.period_id == period_id,
            ReportingPeriod.tenant_id == tenant_id,
        )
        .one_or_none()
    )
    if period is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Period not found")
    return PeriodResponse.model_validate(period)


@router.post("/{period_id}/lock", response_model=PeriodResponse)
def lock_period(
    period_id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> PeriodResponse:
    """Lock a period to prevent further ingestion or modification."""
    period = (
        db.query(ReportingPeriod)
        .filter(
            ReportingPeriod.period_id == period_id,
            ReportingPeriod.tenant_id == tenant_id,
        )
        .one_or_none()
    )
    if period is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Period not found")
    if period.status == PeriodStatus.locked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Period is already locked",
        )
    period.status = PeriodStatus.locked
    db.commit()
    db.refresh(period)
    return PeriodResponse.model_validate(period)
