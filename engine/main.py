"""Engine service — exposes the IFRS 10 calculator via HTTP."""

from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from calculator import IfrsCalculator
from models import EliminationEntry, EntityNode, LedgerEntrySnapshot

app = FastAPI(
    title="Consolidator Engine",
    description="IFRS 10 stateless consolidation calculator.",
    version="0.1.0",
)


class ConsolidationRequest(BaseModel):
    entries: List[LedgerEntrySnapshot]
    entities: List[EntityNode]
    as_of: datetime = None


class ConsolidationResponse(BaseModel):
    eliminations: List[EliminationEntry]
    count: int


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/consolidate", response_model=ConsolidationResponse)
async def consolidate(req: ConsolidationRequest) -> ConsolidationResponse:
    """Run IFRS 10 elimination logic on the provided ledger snapshot."""
    as_of = req.as_of or datetime.now(timezone.utc)
    eliminations = IfrsCalculator.eliminate(req.entries, req.entities, as_of=as_of)
    return ConsolidationResponse(eliminations=eliminations, count=len(eliminations))
