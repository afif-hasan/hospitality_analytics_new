from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.modules.transactions.schemas import (
    BulkCreateRequest,
    CSVUploadResult,
    PaginatedTransactions,
    TransactionCreate,
    TransactionOut,
)
from app.modules.transactions.service import TransactionService

router = APIRouter()


@router.post(
    "/",
    response_model=TransactionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add a single transaction",
)
async def create_transaction(
    payload: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_user),
):
    return await TransactionService.create_one(db, payload)


@router.post(
    "/bulk",
    response_model=list[TransactionOut],
    status_code=status.HTTP_201_CREATED,
    summary="Add multiple transactions at once",
)
async def create_bulk(
    payload: BulkCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_user),
):
    return await TransactionService.create_bulk(db, payload.transactions)


@router.post(
    "/upload-csv",
    response_model=CSVUploadResult,
    status_code=status.HTTP_200_OK,
    summary="Upload transactions via CSV file",
)
async def upload_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_user),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .csv files are accepted",
        )
    file_bytes = await file.read()
    return await TransactionService.bulk_from_csv(db, file_bytes)


@router.get(
    "/",
    response_model=PaginatedTransactions,
    status_code=status.HTTP_200_OK,
    summary="List transactions with optional filters and pagination",
)
async def get_transactions(
    category: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_user),
):
    return await TransactionService.get_all(
        db, category, start_date, end_date, skip, limit
    )