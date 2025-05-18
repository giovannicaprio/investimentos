from fastapi import APIRouter, HTTPException
from app.services.stock_service import StockService

router = APIRouter()
stock_service = StockService()

@router.get("/api/validate_ticker/{ticker}")
async def validate_ticker(ticker: str):
    is_valid, message = stock_service.validate_ticker(ticker)
    return {"valid": is_valid, "message": message}

@router.get("/api/stock_info/{ticker}")
async def get_stock_info(ticker: str):
    stock_info = stock_service.get_stock_info(ticker)
    if stock_info:
        return stock_info
    raise HTTPException(status_code=404, detail="Stock not found") 