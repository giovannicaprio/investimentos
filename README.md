# Projeto Financeiro

## Overview
Este projeto é uma aplicação web para gerenciamento de investimentos. Ele permite que os usuários importem dados de investimentos a partir de arquivos CSV, visualizem e editem seus investimentos, e acompanhem o desempenho de seus ativos.

## Funcionalidades
- Importação de investimentos via arquivo CSV
- Visualização e edição de investimentos
- Cálculo de retorno esperado e real
- Suporte para diferentes tipos de ativos (ações, FIIs, etc.)

## Tecnologias Utilizadas
- FastAPI
- Uvicorn
- Pandas
- Jinja2
- HTML/CSS/JavaScript

## Instruções para Rodar

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/giovannicaprio/investimentos.git
   cd investimentos
   git checkout public
   ```

2. Crie um ambiente virtual e ative-o:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### Executando a Aplicação
1. Inicie o servidor:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Acesse a aplicação em seu navegador:
   ```
   http://127.0.0.1:8000
   ```

## Estrutura do Projeto
- `app/`: Diretório principal da aplicação
  - `importers/`: Módulos para importação de dados
  - `models/`: Definições de modelos de dados
  - `templates/`: Templates HTML
  - `static/`: Arquivos estáticos (CSS, JS, etc.)
  - `main.py`: Ponto de entrada da aplicação

## Contribuição
Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar um Pull Request.

## Licença
Este projeto está licenciado sob a licença MIT.

## Uso do Arquivo run.sh

Para facilitar a execução da aplicação, você pode usar o script `run.sh`. Este script automatiza o processo de ativação do ambiente virtual e inicialização do servidor.

### Como Usar
1. Certifique-se de que o arquivo `run.sh` tem permissão de execução:
   ```bash
   chmod +x run.sh
   ```

2. Execute o script:
   ```bash
   ./run.sh
   ```

O script irá ativar o ambiente virtual e iniciar o servidor da aplicação automaticamente. 