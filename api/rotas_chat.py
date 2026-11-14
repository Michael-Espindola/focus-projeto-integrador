from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.dependencias import obter_usuario_atual
from controllers.tarefa_controller import TarefaController
from services.chatbot import IAIndisponivelError, perguntar_ao_murphy
from services.usuario_service import ESTILOS_VALIDOS

router = APIRouter(prefix="/api/chat", tags=["chat"])
tarefas = TarefaController()


class MensagemHistorico(BaseModel):
    papel: str  # "user" ou "model"
    texto: str


class MensagemChat(BaseModel):
    comando: str
    estilo: Optional[str] = None
    historico: List[MensagemHistorico] = []
    salvar_como_tarefa: bool = False
    titulo_tarefa: Optional[str] = None


@router.post("")
def interagir_chat(dados: MensagemChat, usuario: dict = Depends(obter_usuario_atual)):
    comando = (dados.comando or "").strip()
    if not comando:
        raise HTTPException(status_code=422, detail="Escreva uma mensagem para o Murphy.")

    estilo = dados.estilo if dados.estilo in ESTILOS_VALIDOS else usuario["estilo_instrucao"]

    try:
        resposta = perguntar_ao_murphy(
            comando,
            nome_usuario=usuario["nome"],
            estilo=estilo,
            historico=[m.model_dump() for m in dados.historico],
            usuario_id=usuario["id"],
        )
    except IAIndisponivelError as erro:
        raise HTTPException(status_code=503, detail=str(erro))

    tarefa_salva = False
    if dados.salvar_como_tarefa and dados.titulo_tarefa and dados.titulo_tarefa.strip():
        resultado = tarefas.criar_tarefa(
            titulo=dados.titulo_tarefa, usuario_id=usuario["id"], tipo="IA Murphy",
            descricao=resposta, prioridade="Média", prazo=date.today(),
        )
        tarefa_salva = bool(resultado["sucesso"])

    return {"sucesso": True, "resposta": resposta, "tarefa_salva": tarefa_salva}
