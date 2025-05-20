from datetime import datetime
from typing import List, Dict, Any
import logging
from .csv_importer import CSVImporter
import pandas as pd
from app.models import Investment
from app.database import get_investments, update_investment

logger = logging.getLogger(__name__)

class PosicaoAtualImporter(CSVImporter):
    """Importador específico para o arquivo de posição atual"""
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.required_columns = [
            'Ticker', 'Posição', '% Alocação', 'Rentabilidade c/ proventos',
            'Rentabilidade Bruta', 'Preço médio (abertura)', 'Última cotação',
            'Quantidade de Cotas'
        ]
        # Força a leitura correta do arquivo com separador ;
        try:
            self.data = pd.read_csv(self.file_path, encoding='utf-8', sep=';')
            logger.info(f"Arquivo lido com sucesso usando encoding utf-8 e separador ';'")
            logger.info(f"Colunas detectadas: {list(self.data.columns)}")
            if not all(col in self.data.columns for col in self.required_columns):
                logger.error(f"Colunas obrigatórias ausentes: {self.required_columns}")
            # Log da primeira linha para depuração
            if not self.data.empty:
                logger.info(f"Primeira linha de dados: {self.data.iloc[0].to_dict()}")
        except Exception as e:
            logger.error(f"Erro ao ler arquivo de posição atual: {str(e)}")
            self.data = None
    
    def _convert_currency(self, value: str) -> float:
        """Converte string de valor monetário para float"""
        try:
            # Remove R$, espaços e substitui vírgula por ponto
            value = value.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.').strip()
            return float(value)
        except (ValueError, AttributeError):
            return 0.0
    
    def _convert_percentage(self, value: str) -> float:
        """Converte string de porcentagem para float"""
        try:
            # Remove % e substitui vírgula por ponto
            value = value.replace('%', '').replace(' ', '').replace('.', '').replace(',', '.').strip()
            return float(value)
        except (ValueError, AttributeError):
            return 0.0
    
    def convert_data(self) -> List[Investment]:
        """Converte os dados do arquivo de posição atual"""
        records = []
        if self.data is None:
            return records
        for _, row in self.data.iterrows():
            try:
                converted_record = {}
                converted_record['name'] = row['Ticker']
                ticker = row['Ticker']
                if isinstance(ticker, str) and ticker.endswith('11'):
                    converted_record['type'] = 'fii'
                else:
                    converted_record['type'] = 'acao'
                position = self._convert_currency(str(row['Posição']))
                avg_price = self._convert_currency(str(row['Preço médio (abertura)']))
                current_price = self._convert_currency(str(row['Última cotação']))
                quantidade_raw = row['Quantidade de Cotas']
                if isinstance(quantidade_raw, (int, float)):
                    quantity = int(quantidade_raw) if not pd.isna(quantidade_raw) else 0
                else:
                    quantity_str = str(quantidade_raw).replace('.', '').replace(',', '.').strip()
                    quantity = int(float(quantity_str)) if quantity_str and quantity_str != '-' else 0
                rentabilidade = self._convert_percentage(str(row['Rentabilidade c/ proventos']))
                purchase = {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'quantity': quantity,
                    'price_per_share': avg_price,
                    'total_value': position
                }
                converted_record['purchases'] = [purchase]
                converted_record['current_share_value'] = current_price
                converted_record['expected_return'] = rentabilidade
                converted_record['description'] = f"Importado do arquivo de posição atual em {datetime.now().strftime('%d/%m/%Y')}"
                records.append(Investment(**converted_record))
            except Exception as e:
                logger.error(f"Erro ao converter registro: {str(e)}")
                continue
        return records

    def import_data(self) -> List[Investment]:
        if self.data is None:
            return []
        # Valida se todas as colunas obrigatórias estão presentes
        missing_columns = [col for col in self.required_columns if col not in self.data.columns]
        if missing_columns:
            logger.error(f"Colunas obrigatórias ausentes: {missing_columns}")
            return []
        investments = self.convert_data()
        # Verifica se o ativo já existe e soma as cotas
        for investment in investments:
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
                investments.remove(investment)
        return investments 