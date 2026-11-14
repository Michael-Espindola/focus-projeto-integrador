from controllers.respostas import executar
from services.tarefa_service import TarefaService


def tarefa_para_dict(t) -> dict:
    return {
        "id": t.id,
        "usuario_id": t.usuario_id,
        "titulo": t.titulo,
        "tipo": t.tipo,
        "descricao": t.descricao,
        "prioridade": t.prioridade,
        "prazo": t.prazo.isoformat() if t.prazo else None,
        "concluida": bool(t.concluida),
    }


class TarefaController:

    def __init__(self, service=None):
        self.service = service or TarefaService()

    def listar_tarefas(self, usuario_id: int):
        """Lista somente as tarefas do usuário informado."""
        return executar(
            lambda: [tarefa_para_dict(t) for t in self.service.listar_tarefas_do_usuario(usuario_id)],
            "Tarefas listadas com sucesso!",
            "Não foi possível carregar as tarefas no momento.",
        )

    def buscar_tarefa(self, usuario_id: int, tarefa_id: int):
        return executar(
            lambda: tarefa_para_dict(self.service.buscar_tarefa(usuario_id, tarefa_id)),
            "Tarefa encontrada.",
            "Não foi possível carregar a tarefa.",
        )

    def criar_tarefa(self, titulo, usuario_id=1, tipo=None, descricao=None, prioridade="Média", prazo=None):
        return executar(
            lambda: tarefa_para_dict(self.service.criar_tarefa(
                titulo=titulo, usuario_id=usuario_id, tipo=tipo,
                descricao=descricao, prioridade=prioridade, prazo=prazo)),
            f"Tarefa '{(titulo or '').strip()}' criada com sucesso!",
            "Não foi possível salvar a tarefa no banco de dados.",
        )

    def atualizar_tarefa(self, usuario_id, tarefa_id, titulo, tipo, descricao, prioridade, prazo):
        return executar(
            lambda: tarefa_para_dict(self.service.atualizar_tarefa(
                usuario_id, tarefa_id, titulo, tipo, descricao, prioridade, prazo)),
            "Tarefa atualizada com sucesso!",
            "Não foi possível atualizar a tarefa.",
        )

    def alterar_conclusao(self, usuario_id, tarefa_id, concluida: bool):
        texto = "Tarefa marcada como concluída." if concluida else "Tarefa marcada como pendente."
        return executar(
            lambda: tarefa_para_dict(self.service.alterar_conclusao(usuario_id, tarefa_id, concluida)),
            texto,
            "Não foi possível atualizar o status da tarefa.",
        )

    def excluir_tarefa(self, usuario_id, tarefa_id):
        return executar(
            lambda: self.service.excluir_tarefa(usuario_id, tarefa_id),
            "Tarefa excluída com sucesso.",
            "Não foi possível excluir a tarefa.",
        )

    def excluir_concluidas(self, usuario_id):
        try:
            quantidade = self.service.excluir_concluidas(usuario_id)
        except Exception as erro:
            print("ERRO TÉCNICO:", erro)
            return {"sucesso": False, "tipo": "FALHA_TECNICA",
                    "mensagem": "Não foi possível remover as tarefas concluídas."}
        if quantidade == 0:
            texto = "Não há tarefas concluídas para remover."
        else:
            texto = f"{quantidade} tarefa(s) concluída(s) removida(s)."
        return {"sucesso": True, "tipo": "SUCESSO", "mensagem": texto, "removidas": quantidade}
