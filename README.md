# Plataforma de Equilíbrio de Fases

Plataforma web para simulação de equilíbrio de fases com modelos termodinâmicos integrados (Ideal, NRTL, UNIQUAC, UNIFAC).

## Características

- **Módulo ELV**: Equilíbrio Líquido-Vapor (ponto de bolha, orvalho, flash, diagramas P-xy e T-xy)
- **Módulo ELL**: Equilíbrio Líquido-Líquido (extração, binodais, tie-lines, diagramas ternários)
- **Módulo ESL**: Equilíbrio Sólido-Líquido (solubilidade, cristalização, diagramas)
- **Sistema de autenticação** com Flask-Login
- **Banco de dados SQLite** com SQLAlchemy ORM
- **Interface responsiva** com Bootstrap 5 e Plotly.js

## Tecnologias

- **Backend**: Flask 3.0, Python 3.13
- **Cálculos**: NumPy 2.3, SciPy 1.16, Pandas 2.3
- **Frontend**: HTML5, CSS3, JavaScript ES6+, Bootstrap 5
- **Banco de Dados**: SQLite + SQLAlchemy
- **Segurança**: bcrypt, Flask-Login, CSRF Protection

## Instalação

1. Clone o repositório
2. Crie ambiente virtual: `py -3.13 -m venv venv`
3. Ative o ambiente: `.\venv\Scripts\Activate.ps1`
4. Instale dependências: `pip install -r requirements.txt`
5. Configure .env (copie .env.example)
6. Execute: `python run.py`

## Estrutura do Projeto

plataforma-equilibrio/
├── app/ # Aplicação principal
│ ├── routes/ # Rotas/endpoints
│ ├── thermodynamics/ # Módulos termodinâmicos
│ ├── utils/ # Utilitários
│ ├── static/ # CSS, JS, imagens
│ └── templates/ # Templates HTML
├── data/ # Dados de componentes e parâmetros
├── tests/ # Testes unitários
├── config.py # Configurações
└── run.py # Ponto de entrada

text

## Uso

```bash
# Modo desenvolvimento
python run.py

# Acessar em: http://localhost:5000
Autor
Carlos Eduardo Nunes de Oliveira
Engenharia Química - UFAL
TCC 2025
