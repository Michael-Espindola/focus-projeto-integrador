"""Configuração da conexão com o banco de dados (MySQL por padrão)."""
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Lê o arquivo .env (senhas e chaves ficam fora do código).
# override=True: o .env sempre vence variáveis antigas que existam no Windows.
load_dotenv(override=True)

DB_HOST = os.getenv("DB_HOST", "localhost")
if DB_HOST in ("", "0.0.0.0"):  # 0.0.0.0 não serve para conectar ao MySQL
    DB_HOST = "127.0.0.1"
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "organizacao_db")

# Opcional: DATABASE_URL no .env sobrescreve tudo (útil para testes com SQLite).
# quote_plus protege senhas que tenham caracteres especiais (@, :, /, etc.).
DATABASE_URL = os.getenv("DATABASE_URL") or (
    f"mysql+mysqlconnector://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# pool_pre_ping testa a conexão antes de usar (evita erro de conexão "morta").
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# Classe base de onde todos os models (tabelas) herdam.
Base = declarative_base()