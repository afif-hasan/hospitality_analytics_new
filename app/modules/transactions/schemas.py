from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, ConfigDict


class TransactionCreate(BaseModel):
    property_name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=60)
    price: float = Field(gt=0, description="Must be greater than 0")
    quantity: int = Field(gt=0, description="Must be greater than 0")
    date: date


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_name: str
    category: str
    price: float
    quantity: float
    date: date
    created_at: datetime


class BulkCreateRequest(BaseModel):
    transactions: list[TransactionCreate] = Field(
        min_length=1,
        description="List of transactions to insert"
    )


class CSVRowError(BaseModel):
    row: int
    error: str


class CSVUploadResult(BaseModel):
    imported: int
    skipped: int
    errors: list[CSVRowError]


class TransactionFilter(BaseModel):
    category: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class PaginatedTransactions(BaseModel):
    items: list[TransactionOut]
    total: int
    skip: int
    limit: int