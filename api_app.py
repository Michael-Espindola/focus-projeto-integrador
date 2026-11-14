from dotenv import load_dotenv

load_dotenv()

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from api.rotas_chat import router as rotas_chat
from api.rotas_tarefas import router as rotas_tarefas
from api.rotas_usuarios import router as rotas_usuarios
from config.database import Base, engine
from models import tarefas, usuario  # noqa: F401  (registra as tabelas no SQLAlchemy)

# Cria as tabelas que ainda não existirem. Se o MySQL estiver desligado, avisa com clareza.
try:
    Base.metadata.create_all(bind=engine)
except Exception as erro:
    print("\nERRO: não foi possível conectar ao banco de dados. Verifique se o MySQL está ligado")
    print("e se DB_HOST, DB_PORT, DB_USER, DB_PASSWORD e DB_NAME estão corretos no arquivo .env.")
    print(f"Detalhe técnico: {erro}\n")
    raise

app = FastAPI(title="FOCUS API", version="3.0")

# A autenticação usa o cabeçalho Authorization (não cookies), então não precisa de credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_NOMES_DOS_CAMPOS = {
    "titulo": "título", "tipo": "categoria", "prioridade": "prioridade", "prazo": "prazo",
    "descricao": "descrição", "nome": "nome", "email": "e-mail", "senha": "senha",
    "estilo_instrucao": "estilo", "comando": "mensagem", "username": "usuário", "password": "senha",
    "concluida": "status da tarefa",
}


@app.exception_handler(RequestValidationError)
async def erro_de_validacao(request: Request, erro: RequestValidationError):
    """Transforma os erros de validação do FastAPI em uma mensagem simples em português."""
    primeiro = erro.errors()[0] if erro.errors() else {}
    campo = next((str(p) for p in reversed(primeiro.get("loc", ())) if isinstance(p, str)), "")
    nome = _NOMES_DOS_CAMPOS.get(campo, campo or "dados enviados")
    if primeiro.get("type") == "missing":
        mensagem = f"O campo {nome} é obrigatório."
    elif campo == "prazo":
        mensagem = "Prazo inválido. Use o formato AAAA-MM-DD (ex.: 2026-12-31)."
    else:
        mensagem = f"O valor informado em {nome} é inválido."
    return JSONResponse(status_code=422, content={"detail": mensagem})


@app.get("/")
def home():
    return {
        "mensagem": "API do FOCUS funcionando perfeitamente!",
        "documentacao": "/docs",
        "telas_mobile": "/mobile/telainicial.html",
        "telas_desktop": "/desktop/telainicialDesktop.html",
    }


app.include_router(rotas_usuarios)
app.include_router(rotas_tarefas)
app.include_router(rotas_chat)

# Serve as telas pelo próprio servidor (opcional): http://127.0.0.1:8000/desktop/telainicialDesktop.html
_RAIZ = Path(__file__).resolve().parent
for _pasta, _rota in (("telas_mobile", "/mobile"), ("telas_desktop", "/desktop")):
    if (_RAIZ / _pasta).is_dir():
        app.mount(_rota, StaticFiles(directory=_RAIZ / _pasta, html=True), name=_pasta)
