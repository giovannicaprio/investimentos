from typing import List, Optional
from datetime import datetime
from .models import Investment, Purchase

# Banco de dados em memória
_investments: List[Investment] = []
_purchases: List[Purchase] = []
_next_id = 1
_next_purchase_id = 1

def get_investments() -> List[Investment]:
    """Retorna a lista de investimentos"""
    return _investments

def get_purchases() -> List[Purchase]:
    """Retorna a lista de compras"""
    return _purchases

def get_investment(id: int) -> Optional[Investment]:
    """Retorna um investimento específico"""
    for investment in _investments:
        if investment.id == id:
            return investment
    return None

def create_investment(investment: Investment) -> Investment:
    """Adiciona um novo investimento"""
    global _next_id, _next_purchase_id
    
    # Set investment ID
    investment.id = _next_id
    _next_id += 1
    
    # Set purchase IDs and link them to the investment
    for purchase in investment.purchases:
        purchase.id = _next_purchase_id
        purchase.investment_id = investment.id
        _next_purchase_id += 1
        _purchases.append(purchase)
    
    _investments.append(investment)
    return investment

def update_investment(id: int, investment: Investment) -> Optional[Investment]:
    """Atualiza um investimento existente"""
    for i, existing in enumerate(_investments):
        if existing.id == id:
            investment.id = id
            
            # Atualizar compras
            for purchase in investment.purchases:
                if purchase.id is None:
                    # Nova compra
                    purchase.id = _next_purchase_id
                    purchase.investment_id = id
                    _next_purchase_id += 1
                    _purchases.append(purchase)
                else:
                    # Atualizar compra existente
                    for j, existing_purchase in enumerate(_purchases):
                        if existing_purchase.id == purchase.id:
                            _purchases[j] = purchase
                            break
            
            _investments[i] = investment
            return investment
    return None

def delete_investment(id: int) -> bool:
    """Remove um investimento e suas compras"""
    for i, investment in enumerate(_investments):
        if investment.id == id:
            # Remover compras relacionadas
            _purchases[:] = [p for p in _purchases if p.investment_id != id]
            _investments.pop(i)
            return True
    return False

def get_purchase(id: int) -> Optional[Purchase]:
    """Retorna uma compra específica"""
    for purchase in _purchases:
        if purchase.id == id:
            return purchase
    return None

def create_purchase(purchase: Purchase) -> Purchase:
    """Adiciona uma nova compra"""
    global _next_purchase_id
    purchase.id = _next_purchase_id
    _next_purchase_id += 1
    _purchases.append(purchase)
    return purchase

def update_purchase(id: int, purchase: Purchase) -> Optional[Purchase]:
    """Atualiza uma compra existente"""
    for i, existing in enumerate(_purchases):
        if existing.id == id:
            purchase.id = id
            _purchases[i] = purchase
            return purchase
    return None

def delete_purchase(id: int) -> bool:
    """Remove uma compra"""
    for i, purchase in enumerate(_purchases):
        if purchase.id == id:
            _purchases.pop(i)
            return True
    return False 