from datetime import date

from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.transactions.model import Transaction
from app.modules.analytics.schemas import (
    TotalSalesOut,
    TopPropertyOut,
    CategoryBreakdownOut,
)


class AnalyticsService:

    @staticmethod
    async def get_total_sales(
        db: AsyncSession,
        start_date: date | None,
        end_date: date | None,
    ) -> TotalSalesOut:
        revenue_expr = func.sum(Transaction.price * Transaction.quantity)
        count_expr = func.count(Transaction.id)

        query = select(revenue_expr, count_expr)

        if start_date:
            query = query.where(Transaction.date >= start_date)
        if end_date:
            query = query.where(Transaction.date <= end_date)

        result = await db.execute(query)
        row = result.one()

        total_revenue = float(row[0] or 0)
        total_transactions = int(row[1] or 0)
        average_order_value = (
            round(total_revenue / total_transactions, 2)
            if total_transactions > 0
            else 0.0
        )

        return TotalSalesOut(
            total_revenue=round(total_revenue, 2),
            total_transactions=total_transactions,
            average_order_value=average_order_value,
        )

    @staticmethod
    async def get_top_properties(
        db: AsyncSession,
        start_date: date | None,
        end_date: date | None,
    ) -> list[TopPropertyOut]:
        revenue_expr = func.sum(
            Transaction.price * Transaction.quantity
        ).label("total_revenue")
        count_expr = func.count(Transaction.id).label("total_transactions")

        query = (
            select(
                Transaction.property_name,
                revenue_expr,
                count_expr,
            )
            .group_by(Transaction.property_name)
            .order_by(desc("total_revenue"))
            .limit(3)
        )

        if start_date:
            query = query.where(Transaction.date >= start_date)
        if end_date:
            query = query.where(Transaction.date <= end_date)

        result = await db.execute(query)
        rows = result.all()

        return [
            TopPropertyOut(
                rank=i + 1,
                property_name=row.property_name,
                total_revenue=round(float(row.total_revenue), 2),
                total_transactions=int(row.total_transactions),
            )
            for i, row in enumerate(rows)
        ]

    @staticmethod
    async def get_category_breakdown(
        db: AsyncSession,
        start_date: date | None,
        end_date: date | None,
    ) -> list[CategoryBreakdownOut]:
        revenue_expr = func.sum(
            Transaction.price * Transaction.quantity
        ).label("total_revenue")
        count_expr = func.count(Transaction.id).label("total_transactions")

        query = (
            select(
                Transaction.category,
                revenue_expr,
                count_expr,
            )
            .group_by(Transaction.category)
            .order_by(desc("total_revenue"))
        )

        if start_date:
            query = query.where(Transaction.date >= start_date)
        if end_date:
            query = query.where(Transaction.date <= end_date)

        result = await db.execute(query)
        rows = result.all()

        return [
            CategoryBreakdownOut(
                category=row.category,
                total_revenue=round(float(row.total_revenue), 2),
                total_transactions=int(row.total_transactions),
            )
            for row in rows
        ]