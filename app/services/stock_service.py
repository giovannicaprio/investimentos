import csv
import os
from typing import List, Dict

class StockService:
    def __init__(self):
        self.csv_file = 'app/data/ibovespa_tickers.csv'

    def get_all_tickers(self) -> List[Dict]:
        """
        Lê todos os tickers do arquivo CSV e retorna uma lista de dicionários.
        """
        tickers = []
        if os.path.exists(self.csv_file):
            with open(self.csv_file, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    tickers.append(row)
        return tickers

    def validate_ticker(self, ticker: str) -> bool:
        """
        Valida se o ticker existe no CSV.
        """
        tickers = self.get_all_tickers()
        return any(t['ticker'].upper() == ticker.upper() for t in tickers)

    def get_ticker_info(self, ticker: str) -> Dict:
        """
        Retorna as informações do ticker a partir do CSV.
        """
        tickers = self.get_all_tickers()
        for t in tickers:
            if t['ticker'].upper() == ticker.upper():
                return t
        return {} 