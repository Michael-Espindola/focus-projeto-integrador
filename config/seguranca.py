"""Senhas com hash (PBKDF2) e tokens JWT.

Usa apenas a biblioteca padrão do Python para o hash (nenhuma dependência extra).
"""
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()

ALGORITHM = "HS256"
JWT_SECRET = os.getenv("JWT_SECRET") or "chave_secreta_padrao_segura"
if JWT_SECRET == "chave_secreta_padrao_segura":
    print("AVISO: defina um JWT_SECRET forte no arquivo .env antes de publicar o sistema.")

try:
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES") or 480)
except ValueError:
    JWT_EXPIRE_MINUTES = 480

_PREFIXO = "pbkdf2_sha256"
_ITERACOES = 240_000


def gerar_hash_senha(senha: str) -> str:
    """Gera 'pbkdf2_sha256$iteracoes$sal$hash' (cabe nos 255 caracteres da coluna)."""
    sal = secrets.token_hex(16)
    derivado = hashlib.pbkdf2_hmac("sha256", senha.encode(), bytes.fromhex(sal), _ITERACOES).hex()
    return f"{_PREFIXO}${_ITERACOES}${sal}${derivado}"


def senha_tem_hash(armazenada: str) -> bool:
    return bool(armazenada) and armazenada.startswith(_PREFIXO + "$")


def verificar_senha(senha: str, armazenada: str) -> bool:
    """Confere a senha. Aceita senhas antigas em texto puro (e o login as converte em hash)."""
    if not armazenada:
        return False
    if senha_tem_hash(armazenada):
        try:
            _, iteracoes, sal, esperado = armazenada.split("$")
            derivado = hashlib.pbkdf2_hmac(
                "sha256", senha.encode(), bytes.fromhex(sal), int(iteracoes)
            ).hex()
            return hmac.compare_digest(derivado, esperado)
        except (ValueError, TypeError):
            return False
    return hmac.compare_digest(senha.encode(), armazenada.encode())


def criar_token(usuario) -> str:
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": usuario.nome,
        "id": usuario.id,
        "papel": usuario.papel,
        "iat": agora,
        "exp": agora + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def decodificar_token(token: str) -> dict:
    """Levanta jwt.ExpiredSignatureError (expirado) ou jwt.PyJWTError (inválido)."""
    return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
