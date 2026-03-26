"""Entity management API router.

Endpoints:
  POST   /entities               — create entity
  GET    /entities               — list all entities
  GET    /entities/tree          — full ownership tree as nested JSON
  GET    /entities/{entity_id}   — get single entity
  PATCH  /entities/{entity_id}   — update ownership_pct or parent
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import EntityMetadata

router = APIRouter(prefix="/entities", tags=["entities"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class EntityCreate(BaseModel):
    name: str = Field(..., description="Human-readable entity name")
    parent_entity_id: Optional[uuid.UUID] = Field(None, description="Parent entity UUID; omit for ultimate parent")
    ownership_pct: Optional[Decimal] = Field(None, ge=0, le=100, description="Parent's ownership percentage (0–100)")


class EntityUpdate(BaseModel):
    parent_entity_id: Optional[uuid.UUID] = None
    ownership_pct: Optional[Decimal] = Field(None, ge=0, le=100)


class EntityResponse(BaseModel):
    entity_id: uuid.UUID
    name: str
    parent_entity_id: Optional[uuid.UUID]
    ownership_pct: Optional[Decimal]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(body: EntityCreate, db: Session = Depends(get_db)) -> EntityResponse:
    """Register a new entity in the consolidation hierarchy."""
    if body.parent_entity_id is not None:
        parent = db.get(EntityMetadata, body.parent_entity_id)
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent entity {body.parent_entity_id} not found",
            )

    entity = EntityMetadata(
        name=body.name,
        parent_entity_id=body.parent_entity_id,
        ownership_pct=body.ownership_pct,
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return EntityResponse.model_validate(entity)


@router.get("", response_model=List[EntityResponse])
def list_entities(db: Session = Depends(get_db)) -> List[EntityResponse]:
    """Return all registered entities."""
    rows = db.query(EntityMetadata).all()
    return [EntityResponse.model_validate(r) for r in rows]


@router.get("/tree", response_model=List[Dict[str, Any]])
def entity_tree(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Return the full ownership hierarchy as a nested tree.

    Each node has: entity_id, name, ownership_pct, children[].
    Top-level nodes (parent_entity_id is NULL) are roots.
    """
    rows = db.query(EntityMetadata).all()
    by_id: Dict[uuid.UUID, Dict[str, Any]] = {
        r.entity_id: {
            "entity_id": str(r.entity_id),
            "name": r.name,
            "ownership_pct": str(r.ownership_pct) if r.ownership_pct is not None else None,
            "children": [],
        }
        for r in rows
    }
    roots: List[Dict[str, Any]] = []
    for r in rows:
        node = by_id[r.entity_id]
        if r.parent_entity_id is None:
            roots.append(node)
        else:
            parent = by_id.get(r.parent_entity_id)
            if parent is not None:
                parent["children"].append(node)
    return roots


@router.get("/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: uuid.UUID, db: Session = Depends(get_db)) -> EntityResponse:
    """Return a single entity by UUID."""
    entity = db.get(EntityMetadata, entity_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return EntityResponse.model_validate(entity)


@router.patch("/{entity_id}", response_model=EntityResponse)
def update_entity(
    entity_id: uuid.UUID,
    body: EntityUpdate,
    db: Session = Depends(get_db),
) -> EntityResponse:
    """Update an entity's parent or ownership percentage."""
    entity = db.get(EntityMetadata, entity_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")

    if body.parent_entity_id is not None:
        parent = db.get(EntityMetadata, body.parent_entity_id)
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent entity {body.parent_entity_id} not found",
            )
        entity.parent_entity_id = body.parent_entity_id

    if body.ownership_pct is not None:
        entity.ownership_pct = body.ownership_pct

    db.commit()
    db.refresh(entity)
    return EntityResponse.model_validate(entity)


@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entity(entity_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    """Delete an entity. Blocked if the entity has ledger entries."""
    entity = db.get(EntityMetadata, entity_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    if entity.ledger_entries:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Entity {entity.name!r} has {len(entity.ledger_entries)} ledger entries and cannot be deleted.",
        )
    db.delete(entity)
    db.commit()
