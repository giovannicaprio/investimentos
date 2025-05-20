import csv
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging
from ..models import Investment

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVImporter:
    """Classe base para importação de arquivos CSV"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.data = None
        self.required_columns = []
        self.column_mapping = {}
        
    def validate_file(self) -> bool:
        """Valida se o arquivo existe e é um CSV válido"""
        if not self.file_path.exists():
            logger.error(f"Arquivo não encontrado: {self.file_path}")
            return False
            
        if self.file_path.suffix.lower() != '.csv':
            logger.error(f"Arquivo não é um CSV: {self.file_path}")
            return False
            
        return True
        
    def read_file(self) -> bool:
        """Lê o arquivo CSV e armazena os dados"""
        try:
            # Tenta diferentes encodings e separadores
            encodings = ['utf-8', 'latin1', 'iso-8859-1']
            for encoding in encodings:
                try:
                    # Primeiro tenta com separador padrão (vírgula)
                    try:
                        self.data = pd.read_csv(self.file_path, encoding=encoding)
                        logger.info(f"Arquivo lido com sucesso usando encoding {encoding} e separador padrão (',')")
                        return True
                    except Exception:
                        # Se falhar, tenta com separador ponto e vírgula
                        self.data = pd.read_csv(self.file_path, encoding=encoding, sep=';')
                        logger.info(f"Arquivo lido com sucesso usando encoding {encoding} e separador ';'")
                        return True
                except UnicodeDecodeError:
                    continue
            logger.error("Não foi possível ler o arquivo com nenhum encoding suportado e separador detectado")
            return False
        except Exception as e:
            logger.error(f"Erro ao ler arquivo CSV: {str(e)}")
            return False
            
    def validate_columns(self) -> bool:
        """Valida se todas as colunas necessárias estão presentes"""
        if self.data is None:
            return False
            
        missing_columns = [col for col in self.required_columns 
                         if col not in self.data.columns]
                         
        if missing_columns:
            logger.error(f"Colunas obrigatórias ausentes: {missing_columns}")
            return False
            
        return True
        
    def map_columns(self) -> None:
        """Mapeia as colunas do CSV para o formato do modelo"""
        if self.data is None:
            return
            
        for csv_col, model_col in self.column_mapping.items():
            if csv_col in self.data.columns:
                self.data[model_col] = self.data[csv_col]
                
    def convert_data(self) -> List[Dict[str, Any]]:
        """Converte os dados para o formato do modelo"""
        if self.data is None:
            return []
            
        return self.data.to_dict('records')
        
    def import_data(self) -> List[Investment]:
        """Importa os dados do CSV para o modelo"""
        if not self.validate_file():
            return []
            
        if not self.read_file():
            return []
            
        if not self.validate_columns():
            return []
            
        self.map_columns()
        records = self.convert_data()
        
        investments = []
        for record in records:
            try:
                # Garante que todos os campos necessários existam
                record.setdefault('description', '')
                record.setdefault('quantity', 1)
                
                # Converte valores numéricos
                for field in ['initial_value', 'current_value', 'expected_return']:
                    if field in record:
                        try:
                            record[field] = float(str(record[field]).replace('R$', '').replace('.', '').replace(',', '.'))
                        except (ValueError, TypeError):
                            logger.error(f"Erro ao converter valor numérico para {field}: {record[field]}")
                            continue
                
                investment = Investment(**record)
                investments.append(investment)
            except Exception as e:
                logger.error(f"Erro ao criar investimento: {str(e)}")
                continue
                
        return investments

class B3CSVImporter(CSVImporter):
    """Importador específico para arquivos CSV da B3"""
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.required_columns = [
            'Ativo',
            'Quantidade',
            'Preço Médio',
            'Preço Atual',
            'Data de Compra'
        ]
        self.column_mapping = {
            'Ativo': 'name',
            'Quantidade': 'quantity',
            'Preço Médio': 'initial_value',
            'Preço Atual': 'current_value',
            'Data de Compra': 'start_date'
        }
        
    def convert_data(self) -> List[Dict[str, Any]]:
        """Converte os dados específicos da B3"""
        records = super().convert_data()
        converted_records = []
        
        for record in records:
            try:
                # Cria um novo dicionário para o registro convertido
                converted_record = {}
                
                # Mantém o nome original sem nenhuma modificação
                converted_record['name'] = record['name']
                logger.info(f"Nome do ativo B3 original: {record['name']}")
                
                # Converte valores monetários
                initial_value = str(record['initial_value']).replace('R$', '').strip()
                current_value = str(record['current_value']).replace('R$', '').strip()
                
                # Trata valores com vírgula
                initial_value = initial_value.replace('.', '').replace(',', '.')
                current_value = current_value.replace('.', '').replace(',', '.')
                
                converted_record['initial_value'] = float(initial_value)
                converted_record['current_value'] = float(current_value)
                
                # Converte quantidade
                converted_record['quantity'] = int(float(str(record['quantity']).replace('.', '').replace(',', '.')))
                
                # Converte data para date
                if isinstance(record['start_date'], str):
                    converted_record['start_date'] = datetime.strptime(record['start_date'], '%d/%m/%Y').date()
                
                # Define tipo como 'Ação' por padrão
                converted_record['type'] = 'Ação'
                
                # Calcula retorno esperado (pode ser personalizado)
                converted_record['expected_return'] = 10.0  # 10% por padrão
                
                # Adiciona descrição vazia por padrão
                converted_record['description'] = ''
                
                logger.info(f"Registro B3 convertido: {converted_record}")
                converted_records.append(converted_record)
                
            except Exception as e:
                logger.error(f"Erro ao converter registro B3: {str(e)}")
                continue
                
        return converted_records

class XPCSVImporter(CSVImporter):
    """Importador específico para arquivos CSV da XP"""
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.required_columns = [
            'Ativo',
            'Quantidade',
            'Preço Médio',
            'Preço Atual',
            'Data',
            'Tipo'
        ]
        self.column_mapping = {
            'Ativo': 'name',
            'Quantidade': 'quantity',
            'Preço Médio': 'initial_value',
            'Preço Atual': 'current_value',
            'Data': 'start_date',
            'Tipo': 'type'
        }
        
    def convert_data(self) -> List[Dict[str, Any]]:
        """Converte os dados específicos da XP"""
        records = super().convert_data()
        converted_records = []
        
        for record in records:
            try:
                # Cria um novo dicionário para o registro convertido
                converted_record = {}
                
                # Mantém o nome original sem nenhuma modificação
                converted_record['name'] = record['name']
                logger.info(f"Nome do ativo XP original: {record['name']}")
                
                # Converte valores monetários
                initial_value = str(record['initial_value']).replace('R$', '').strip()
                current_value = str(record['current_value']).replace('R$', '').strip()
                
                # Trata valores com vírgula
                initial_value = initial_value.replace('.', '').replace(',', '.')
                current_value = current_value.replace('.', '').replace(',', '.')
                
                converted_record['initial_value'] = float(initial_value)
                converted_record['current_value'] = float(current_value)
                
                # Converte quantidade
                converted_record['quantity'] = int(float(str(record['quantity']).replace('.', '').replace(',', '.')))
                
                # Converte data para date
                if isinstance(record['start_date'], str):
                    converted_record['start_date'] = datetime.strptime(record['start_date'], '%d/%m/%Y').date()
                
                # Mantém o tipo original
                converted_record['type'] = str(record['type']).strip()
                
                # Define retorno esperado baseado no tipo
                type_returns = {
                    'Ação': 10.0,
                    'Fundo': 8.0,
                    'Tesouro': 6.0,
                    'CDB': 7.0
                }
                converted_record['expected_return'] = type_returns.get(converted_record['type'], 5.0)
                
                # Adiciona descrição vazia por padrão
                converted_record['description'] = ''
                
                logger.info(f"Registro XP convertido: {converted_record}")
                converted_records.append(converted_record)
                
            except Exception as e:
                logger.error(f"Erro ao converter registro XP: {str(e)}")
                continue
                
        return converted_records

class PosicaoAtualImporter(CSVImporter):
    """Importador específico para o arquivo de posição atual"""
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.required_columns = [
            'Ticker', 'Posição', '% Alocação', 'Rentabilidade c/ proventos',
            'Rentabilidade Bruta', 'Preço médio (abertura)', 'Última cotação',
            'Quantidade de Cotas'
        ]
    
    def convert_data(self) -> List[Dict[str, Any]]:
        """Converte os dados do arquivo de posição atual"""
        records = []
        
        for record in self.data:
            try:
                # Cria um novo dicionário para o registro convertido
                converted_record = {}
                
                # Nome do ativo
                converted_record['name'] = record['Ticker']
                
                # Tipo do ativo (baseado no sufixo)
                ticker = record['Ticker']
                if ticker.endswith('11'):
                    converted_record['type'] = 'fii'
                else:
                    converted_record['type'] = 'acao'
                
                # Converte valores monetários
                position = str(record['Posição']).replace('R$', '').replace('.', '').replace(',', '.').strip()
                avg_price = str(record['Preço médio (abertura)']).replace('R$', '').replace('.', '').replace(',', '.').strip()
                current_price = str(record['Última cotação']).replace('R$', '').replace('.', '').replace(',', '.').strip()
                
                # Converte quantidade
                quantity = str(record['Quantidade de Cotas']).replace('.', '').replace(',', '.').strip()
                
                # Converte rentabilidade
                rentabilidade = str(record['Rentabilidade c/ proventos']).replace('%', '').replace('.', '').replace(',', '.').strip()
                
                # Cria uma compra com os dados
                purchase = {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'quantity': int(float(quantity)),
                    'price_per_share': float(avg_price),
                    'total_value': float(position)
                }
                
                converted_record['purchases'] = [purchase]
                converted_record['current_share_value'] = float(current_price)
                converted_record['expected_return'] = float(rentabilidade) if rentabilidade != '-' else 0.0
                converted_record['description'] = f"Importado do arquivo de posição atual em {datetime.now().strftime('%d/%m/%Y')}"
                
                records.append(converted_record)
                
            except Exception as e:
                logger.error(f"Erro ao converter registro: {str(e)}")
                continue
        
        return records

def get_importer(file_path: str) -> Optional[CSVImporter]:
    """Factory para criar o importador apropriado baseado no nome do arquivo"""
    file_name = Path(file_path).name.lower()
    
    if 'b3' in file_name:
        return B3CSVImporter(file_path)
    elif 'xp' in file_name:
        return XPCSVImporter(file_path)
    elif 'posicao_atual' in file_name:
        return PosicaoAtualImporter(file_path)
    else:
        logger.error(f"Formato de arquivo não suportado: {file_name}")
        return None 