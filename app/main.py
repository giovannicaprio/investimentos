from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from datetime import date, datetime
from app.models import Investment, Purchase
from typing import List
from pydantic import BaseModel
from pathlib import Path
import shutil
from app.database import (
    get_investments, get_investment, create_investment, update_investment, delete_investment,
    get_purchases, get_purchase, create_purchase, update_purchase, delete_purchase
)
from app.importers import get_importer
from .services.stock_service import StockService
from app.services.stock_service import StockService
from app.routes import router as stock_router
from app.importers.posicao_atual_importer import PosicaoAtualImporter
import logging

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include stock routes
app.include_router(stock_router)

# Get the current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Configuração do diretório de uploads
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/edit", response_class=HTMLResponse)
async def edit_page(request: Request):
    return templates.TemplateResponse("edit.html", {"request": request})

@app.get("/api/investments", response_model=List[Investment])
async def get_investments_route():
    return get_investments()

@app.get("/api/investments/{investment_id}", response_model=Investment)
async def get_investment_route(investment_id: int):
    try:
        return get_investment(investment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/investments", response_model=Investment)
async def create_investment_route(investment: Investment):
    # Verifica se o ativo já existe baseado no ticker
    existing_investment = next((inv for inv in get_investments() if inv.name == investment.name), None)
    if existing_investment:
        # Soma as cotas e recalcula o preço médio
        total_quantity = existing_investment.total_quantity + investment.total_quantity
        total_value = existing_investment.initial_value + investment.initial_value
        avg_price = total_value / total_quantity if total_quantity > 0 else 0
        existing_investment.purchases.extend(investment.purchases)
        existing_investment.current_share_value = investment.current_share_value
        existing_investment.expected_return = investment.expected_return
        existing_investment.description = investment.description
        # Atualiza o investimento existente
        update_investment(existing_investment.id, existing_investment)
        return existing_investment
    return create_investment(investment)

@app.put("/api/investments/{investment_id}", response_model=Investment)
async def update_investment_route(investment_id: int, updated_investment: Investment):
    try:
        # Manter o ID original
        updated_investment.id = investment_id
        # Atualizar a data de última atualização
        updated_investment.last_update = datetime.now()
        # Manter a data de início original
        original = get_investment(investment_id)
        updated_investment.start_date = original.start_date
        
        update_investment(investment_id, updated_investment)
        return updated_investment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/api/investments/{investment_id}")
async def delete_investment_route(investment_id: int):
    try:
        delete_investment(investment_id)
        return {"message": "Investimento excluído com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/import")
async def import_investments_route(file: UploadFile = File(...)):
    try:
        # Salva o arquivo temporariamente
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Usa o importador específico para posição atual
        importer = PosicaoAtualImporter(file_path)
        investments = importer.import_data()
        
        # Remove o arquivo temporário
        os.remove(file_path)
        
        if not investments:
            raise HTTPException(status_code=400, detail="Nenhum investimento válido encontrado no arquivo")
        
        # Log detalhado dos investimentos processados
        logger.info(f"Investimentos processados: {investments}")
        
        # Salva os investimentos no banco de dados
        for investment in investments:
            try:
                create_investment(investment)
            except Exception as e:
                logger.error(f"Erro ao criar investimento: {str(e)}")
        
        return {"message": f"{len(investments)} investimentos importados com sucesso"}
        
    except Exception as e:
        logger.error(f"Erro ao importar arquivo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stocks/{ticker}")
async def get_stock_info(ticker: str):
    """Obtém informações de uma ação específica"""
    info = StockService.get_stock_info(ticker)
    if info is None:
        raise HTTPException(status_code=404, detail="Ação não encontrada")
    return info

@app.get("/api/stocks/{ticker}/price")
async def get_stock_price(ticker: str):
    """Obtém apenas o preço atual de uma ação"""
    price = StockService.get_current_price(ticker)
    if price is None:
        raise HTTPException(status_code=404, detail="Ação não encontrada")
    return {"price": price}

@app.get("/api/stocks/{ticker}/validate")
async def validate_stock(ticker: str):
    """Valida se um ticker existe e está disponível"""
    is_valid = StockService.validate_ticker(ticker)
    return {"valid": is_valid}

@app.get("/api/purchases", response_model=List[Purchase])
async def get_purchases_route():
    return get_purchases()

@app.get("/api/purchases/{purchase_id}", response_model=Purchase)
async def get_purchase_route(purchase_id: int):
    try:
        return get_purchase(purchase_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/purchases", response_model=Purchase)
async def create_purchase(purchase: Purchase):
    add_purchase(purchase)
    return purchase

@app.put("/api/purchases/{purchase_id}", response_model=Purchase)
async def update_purchase_route(purchase_id: int, updated_purchase: Purchase):
    try:
        # Manter o ID original
        updated_purchase.id = purchase_id
        update_purchase(purchase_id, updated_purchase)
        return updated_purchase
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/api/purchases/{purchase_id}")
async def delete_purchase_route(purchase_id: int):
    try:
        delete_purchase(purchase_id)
        return {"message": "Compra excluída com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/validate_ticker/{ticker}")
async def validate_ticker(ticker: str):
    """Valida se um ticker existe na lista de tickers do Ibovespa"""
    try:
        with open("app/static/data/ibovespa_tickers.csv", "r") as f:
            tickers = [line.split(",")[0] for line in f.readlines()[1:]]  # Skip header
        return {"valid": ticker.upper() in tickers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock_info/{ticker}")
async def get_stock_info(ticker: str):
    """Retorna informações básicas de um ticker"""
    try:
        with open("app/static/data/ibovespa_tickers.csv", "r") as f:
            for line in f.readlines()[1:]:  # Skip header
                ticker_data = line.strip().split(",")
                if ticker_data[0].upper() == ticker.upper():
                    return {
                        "ticker": ticker_data[0],
                        "name": ticker_data[1],
                        "sector": ticker_data[2],
                        "industry": ticker_data[3]
                    }
        raise HTTPException(status_code=404, detail="Ticker não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) 