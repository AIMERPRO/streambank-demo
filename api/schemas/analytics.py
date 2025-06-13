from pydantic import BaseModel


class AverageAmountResponse(BaseModel):
    average_amount: float


class CategoryStats(BaseModel):
    name: str
    total_amount: float
    transaction_count: int


class P95AmountResponse(BaseModel):
    p95_amount: float
