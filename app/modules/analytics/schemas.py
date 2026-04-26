from pydantic import BaseModel


class TotalSalesOut(BaseModel):
    total_revenue: float
    total_transactions: int
    average_order_value: float


class TopPropertyOut(BaseModel):
    rank: int
    property_name: str
    total_revenue: float
    total_transactions: int


class CategoryBreakdownOut(BaseModel):
    category: str
    total_revenue: float
    total_transactions: int