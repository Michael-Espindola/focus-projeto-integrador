from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from api.dependencias import obter_usuario_atual, resolver_resposta, verificar_admin
from controllers.usuario_controller import UsuarioController

router = APIRouter(prefix="/usuarios", tags=["usuarios"])
controller = UsuarioController()


class NovoUsuario(BaseModel):
    nome: str
    email: str
    senha: str
    estilo_instrucao: str = "direto"


class AtualizarUsuario(BaseModel):
    estilo_instrucao: str = "direto"


@router.get("")
def listar_usuarios(usuario: dict = Depends(obter_usuario_atual)):
    return resolver_resposta(controller.listar_usuarios())


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_usuario(dados: NovoUsuario):
    """Cadastro público. O papel é sempre 'usuario' (nunca vem do cliente)."""
    return resolver_resposta(controller.criar_perfil(
        nome=dados.nome, email=dados.email, senha=dados.senha, estilo_instrucao=dados.estilo_instrucao,
    ))


@router.post("/login", status_code=status.HTTP_200_OK)
def fazer_login(form_data: OAuth2PasswordRequestForm = Depends()):
    resposta = resolver_resposta(controller.autenticar_usuario(form_data.username, form_data.password))
    # Achata o resultado para o formato esperado pelas telas.
    return {"sucesso": True, "mensagem": resposta["mensagem"], **resposta["dados"]}


# Rotas fixas ("/perfil/me" e "/me") vêm antes de "/{usuario_id}".
@router.get("/perfil/me")
def ver_perfil_protegido(usuario: dict = Depends(obter_usuario_atual)):
    return {
        "mensagem": "Acesso autorizado com sucesso!",
        "usuario_logado": usuario["nome"],
        "dados": usuario,
    }


@router.patch("/me")
def atualizar_meu_estilo(dados: AtualizarUsuario, usuario: dict = Depends(obter_usuario_atual)):
    return resolver_resposta(controller.atualizar_estilo(usuario["id"], dados.estilo_instrucao))


@router.get("/{usuario_id}")
def buscar_usuario(usuario_id: int, usuario: dict = Depends(obter_usuario_atual)):
    encontrado = controller.buscar_por_id(usuario_id)
    if not encontrado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return encontrado


@router.delete("/{usuario_id}", status_code=200)
def excluir_usuario(usuario_id: int, admin: dict = Depends(verificar_admin)):
    if usuario_id == admin["id"]:
        raise HTTPException(status_code=422, detail="Você não pode excluir a sua própria conta.")
    return resolver_resposta(controller.excluir_perfil(usuario_id))
