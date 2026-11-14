from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from api.dependencias import obter_usuario_atual, resolver_resposta
from controllers.tarefa_controller import TarefaController

router = APIRouter(prefix="/tarefas", tags=["tarefas"])
controller = TarefaController()


class DadosTarefa(BaseModel):
    titulo: str
    tipo: str = "Geral"
    prioridade: str = "Média"
    prazo: Optional[date] = None  # formato AAAA-MM-DD
    descricao: Optional[str] = None


class DadosConclusao(BaseModel):
    concluida: bool


@router.get("")
def listar_tarefas(usuario: dict = Depends(obter_usuario_atual)):
    """Lista somente as tarefas de quem está logado."""
    return resolver_resposta(controller.listar_tarefas(usuario["id"]))


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_tarefa(dados: DadosTarefa, usuario: dict = Depends(obter_usuario_atual)):
    return resolver_resposta(controller.criar_tarefa(
        titulo=dados.titulo, usuario_id=usuario["id"], tipo=dados.tipo,
        descricao=dados.descricao, prioridade=dados.prioridade, prazo=dados.prazo,
    ))


# Atenção: esta rota precisa vir ANTES de "/{tarefa_id}" para "concluidas" não ser lido como número.
@router.delete("/concluidas")
def excluir_concluidas(usuario: dict = Depends(obter_usuario_atual)):
    return resolver_resposta(controller.excluir_concluidas(usuario["id"]))


@router.get("/{tarefa_id}")
def buscar_tarefa(tarefa_id: int, usuario: dict = Depends(obter_usuario_atual)):
    return resolver_resposta(controller.buscar_tarefa(usuario["id"], tarefa_id))


@router.put("/{tarefa_id}")
def atualizar_tarefa(tarefa_id: int, dados: DadosTarefa, usuario: dict = Depends(obter_usuario_atual)):
    return resolver_resposta(controller.atualizar_tarefa(
        usuario["id"], tarefa_id, dados.titulo, dados.tipo, dados.descricao, dados.prioridade, dados.prazo,
    ))


@router.patch("/{tarefa_id}/concluida")
def alterar_conclusao(tarefa_id: int, dados: DadosConclusao, usuario: dict = Depends(obter_usuario_atual)):
    return resolver_resposta(controller.alterar_conclusao(usuario["id"], tarefa_id, dados.concluida))


@router.delete("/{tarefa_id}")
def excluir_tarefa(tarefa_id: int, usuario: dict = Depends(obter_usuario_atual)):
    return resolver_resposta(controller.excluir_tarefa(usuario["id"], tarefa_id))
