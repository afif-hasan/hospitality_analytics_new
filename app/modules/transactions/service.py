import csv
import io
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.transactions.model import Transaction
from app.modules.transactions.schemas import (
    TransactionCreate,
    TransactionOut,
    CSVUploadResult,
    CSVRowError,
    PaginatedTransactions,
)


class TransactionService:

    @staticmethod
    async def create_one(
        db: AsyncSession, payload: TransactionCreate
    ) -> Transaction:
        transaction = Transaction(**payload.model_dump())
        db.add(transaction)
        await db.flush()
        await db.refresh(transaction)
        return transaction

    @staticmethod
    async def create_bulk(
        db: AsyncSession, payloads: list[TransactionCreate]
    ) -> list[Transaction]:
        transactions = [Transaction(**p.model_dump()) for p in payloads]
        db.add_all(transactions)
        await db.flush()
        for t in transactions:
            await db.refresh(t)
        return transactions

    @staticmethod
    async def bulk_from_csv(
        db: AsyncSession, file_bytes: bytes
    ) -> CSVUploadResult:
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File encoding must be UTF-8",
            )

        reader = csv.DictReader(io.StringIO(content))

        required_fields = {"property_name", "category", "price", "quantity", "date"}
        if not required_fields.issubset(set(reader.fieldnames or [])):
            missing = required_fields - set(reader.fieldnames or [])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV missing required columns: {missing}",
            )

        valid: list[Transaction] = []
        errors: list[CSVRowError] = []

        for i, row in enumerate(reader, start=2):
            try:
                payload = TransactionCreate(
                    property_name=row["property_name"].strip(),
                    category=row["category"].strip(),
                    price=float(row["price"]),
                    quantity=int(row["quantity"]),
                    date=date.fromisoformat(row["date"].strip()),
                )
                valid.append(Transaction(**payload.model_dump()))
            except Exception as e:
                errors.append(CSVRowError(row=i, error=str(e)))

        if valid:
            db.add_all(valid)
            await db.flush()

        return CSVUploadResult(
            imported=len(valid),
            skipped=len(errors),
            errors=errors,
        )

    @staticmethod
    async def get_all(
        db: AsyncSession,
        category: str | None,
        start_date: date | None,
        end_date: date | None,
        skip: int,
        limit: int,
    ) -> PaginatedTransactions:
        query = select(Transaction)
        count_query = select(func.count(Transaction.id))

        if category:
            query = query.where(Transaction.category == category)
            count_query = count_query.where(Transaction.category == category)

        if start_date:
            query = query.where(Transaction.date >= start_date)
            count_query = count_query.where(Transaction.date >= start_date)

        if end_date:
            query = query.where(Transaction.date <= end_date)
            count_query = count_query.where(Transaction.date <= end_date)

        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Transaction.date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()

        return PaginatedTransactions(
            items=[TransactionOut.model_validate(t) for t in items],
            total=total,
            skip=skip,
            limit=limit,
        )
    
    