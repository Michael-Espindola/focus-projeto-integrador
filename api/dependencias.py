"""Peças reutilizadas pelas rotas: autenticação e tradução de respostas em erros HTTP."""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from config.seguranca import decodificar_token
from repositories.usuario_repository import UsuarioRepository

# auto_error=False para devolvermos a mensagem em português (e não a padrão em inglês).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login", auto_error=False)

STATUS_POR_TIPO = {
    "REGRA_NEGOCIO": status.HTTP_422_UNPROCESSABLE_ENTITY,
    "NAO_ENCONTRADO": status.HTTP_404_NOT_FOUND,
    "NAO_AUTORIZADO": status.HTTP_401_UNAUTHORIZED,
    "SEM_PERMISSAO": status.HTTP_403_FORBIDDEN,
    "FALHA_TECNICA": status.HTTP_500_INTERNAL_SERVER_ERROR,
}


def resolver_resposta(resposta: dict) -> dict:
    """Se o controller devolveu erro, vira HTTPException; senão devolve a própria resposta."""
    if not resposta.get("sucesso"):
        codigo = STATUS_POR_TIPO.get(resposta.get("tipo"), status.HTTP_400_BAD_REQUEST)
        cabecalhos = {"WWW-Authenticate": "Bearer"} if codigo == 401 else None
        raise HTTPException(status_code=codigo, detail=resposta.get("mensagem"), headers=cabecalhos)
    return resposta


def _nao_autorizado(mensagem: str):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=mensagem,
        headers={"WWW-Authenticate": "Bearer"},
    )


def obter_usuario_atual(token: str = Depends(oauth2_scheme)) -> dict:
    """Valida o token e confere se o usuário ainda existe. Retorna id, nome, papel e estilo."""
    if not token:
        raise _nao_autorizado("Faça login para continuar.")
    try:
        payload = decodificar_token(token)
    except jwt.ExpiredSignatureError:
        raise _nao_autorizado("Sua sessão expirou. Faça login novamente.")
    except jwt.PyJWTError:
        raise _nao_autorizado("Sessão inválida. Faça login novamente.")

    usuario_id = payload.get("id")
    if usuario_id is None:
        raise _nao_autorizado("Sessão inválida. Faça login novamente.")

    usuario = UsuarioRepository().buscar_por_id(usuario_id)
    if not usuario:
        raise _nao_autorizado("Esta conta não existe mais. Faça login novamente.")

    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "papel": usuario.papel,
        "estilo_instrucao": usuario.estilo_instrucao,
    }


def verificar_admin(usuario: dict = Depends(obter_usuario_atual)) -> dict:
    if usuario["papel"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para esta ação.")
    return usuario
