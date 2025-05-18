#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Verificando dependências do sistema...${NC}"

# Verifica e instala dependências do sistema necessárias para o pandas
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo -e "${YELLOW}Instalando dependências para macOS...${NC}"
    brew install python3-dev
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo -e "${YELLOW}Instalando dependências para Linux...${NC}"
    sudo apt-get update
    sudo apt-get install -y python3-dev python3-pip python3-venv build-essential
fi

echo -e "${YELLOW}Verificando ambiente virtual...${NC}"

# Verifica se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Criando ambiente virtual...${NC}"
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Erro ao criar ambiente virtual. Verifique se o python3-venv está instalado.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Ambiente virtual criado com sucesso!${NC}"
fi

# Ativa o ambiente virtual
echo -e "${YELLOW}Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Atualiza pip e instala wheel
echo -e "${YELLOW}Atualizando pip e instalando wheel...${NC}"
pip install --upgrade pip
pip install wheel

# Verifica se o requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo -e "${YELLOW}Criando requirements.txt com dependências básicas...${NC}"
    echo "fastapi==0.68.1
uvicorn==0.15.0
jinja2==3.1.2
python-multipart==0.0.5
aiofiles==23.2.1
pandas==1.3.3
python-dateutil==2.8.2
yfinance==0.2.36" > requirements.txt
    echo -e "${GREEN}requirements.txt criado com sucesso!${NC}"
fi

# Verifica se pandas está no requirements.txt
if ! grep -q "pandas" requirements.txt; then
    echo -e "${YELLOW}Adicionando pandas ao requirements.txt...${NC}"
    echo "pandas==1.3.3" >> requirements.txt
fi

# Verifica se yfinance está no requirements.txt
if ! grep -q "yfinance" requirements.txt; then
    echo -e "${YELLOW}Adicionando yfinance ao requirements.txt...${NC}"
    echo "yfinance==0.2.36" >> requirements.txt
fi

# Instala ou atualiza as dependências
echo -e "${YELLOW}Instalando/atualizando dependências...${NC}"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao instalar dependências. Verifique o arquivo requirements.txt${NC}"
    exit 1
fi

echo -e "${GREEN}Dependências instaladas com sucesso!${NC}"

# Roda a aplicação
echo -e "${YELLOW}Iniciando a aplicação...${NC}"
python -m uvicorn app.main:app --reload

# Desativa o ambiente virtual quando a aplicação for encerrada
deactivate 