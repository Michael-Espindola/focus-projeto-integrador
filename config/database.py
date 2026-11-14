"""Configuração da conexão com o banco de dados (MySQL local ou SQLite/DATABASE_URL na nuvem)."""
import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent

# Lê o arquivo .env sem sobrescrever variáveis já injetadas pelo ambiente (ex.: Render).
load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)

DB_HOST = os.getenv("DB_HOST", "").strip()
if DB_HOST in ("", "0.0.0.0"):
    DB_HOST = "127.0.0.1"

DB_PORT = os.getenv("DB_PORT", "3306").strip()
DB_USER = os.getenv("DB_USER", "root").strip()
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "organizacao_db").strip()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
elif os.getenv("RENDER") or os.getenv("USE_SQLITE", "").lower() == "true" or not os.getenv("DB_HOST"):
    sqlite_path = BASE_DIR / "focus_render.db"
    engine = create_engine(
        f"sqlite:///{sqlite_path}",
        connect_args={"check_same_thread": False},
    )
else:
    # Conexão padrão com o MySQL local no notebook
    mysql_url = (
        f"mysql+mysqlconnector://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    engine = create_engine(mysql_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# Classe base de onde todos os models (tabelas) herdam.
Base = declarative_base()