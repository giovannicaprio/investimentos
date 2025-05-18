from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class Purchase(BaseModel):
    id: Optional[int] = None
    investment_id: Optional[int] = None
    date: str
    quantity: int
    price_per_share: float
    total_value: float
    description: Optional[str] = None

    @property
    def average_price(self) -> float:
        """Retorna o preço médio da compra"""
        return self.price_per_share

class Investment(BaseModel):
    id: Optional[int] = None
    name: str
    type: str  # e.g., "Ações", "FII", "CDB", etc.
    expected_return: float  # em porcentagem
    start_date: Optional[date] = None
    last_update: Optional[date] = None
    description: Optional[str] = None
    purchases: List[Purchase] = []
    current_share_value: Optional[float] = None

    @property
    def total_quantity(self) -> int:
        """Retorna o total de cotas/ações"""
        return sum(purchase.quantity for purchase in self.purchases)

    @property
    def initial_value(self) -> float:
        """Retorna o valor total investido"""
        return sum(purchase.total_value for purchase in self.purchases)

    @property
    def current_value(self) -> float:
        """Retorna o valor atual total"""
        if not self.current_share_value:
            return self.initial_value
        return self.total_quantity * self.current_share_value

    @property
    def average_share_value(self) -> float:
        """Calcula o preço médio das cotas/ações"""
        if not self.total_quantity:
            return 0.0
        return self.initial_value / self.total_quantity

    @property
    def actual_return(self) -> float:
        """Calcula o retorno real baseado no valor inicial e atual"""
        if not self.initial_value:
            return 0.0
        return ((self.current_value - self.initial_value) / self.initial_value) * 100 