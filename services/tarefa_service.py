from repositories.tarefa_repository import TarefaRepository
from services.excecoes import NaoEncontradoError

_PRIORIDADES = {"alta": "Alta", "media": "Média", "média": "Média", "baixa": "Baixa"}


class TarefaService:
    """Regras de negócio das tarefas."""

    def __init__(self, repository=None):
        self.repository = repository or TarefaRepository()

    # ---------- validações ----------
    def _validar(self, titulo, tipo, prioridade, prazo):
        if not titulo or not titulo.strip():
            raise ValueError("O título da tarefa não pode ficar em branco.")
        if len(titulo.strip()) < 3:
            raise ValueError("O título da tarefa deve ter pelo menos 3 caracteres.")
        if not tipo or not tipo.strip():
            raise ValueError("A categoria ou tipo da tarefa não pode ficar em branco.")
        if not prioridade or not prioridade.strip():
            raise ValueError("A prioridade da tarefa deve ser especificada.")
        if prioridade.strip().lower() not in _PRIORIDADES:
            raise ValueError("A prioridade deve ser Alta, Média ou Baixa.")
        if not prazo:
            raise ValueError("O prazo da tarefa é obrigatório.")
        return titulo.strip(), tipo.strip(), _PRIORIDADES[prioridade.strip().lower()]

    def _buscar_do_usuario(self, usuario_id: int, tarefa_id: int):
        tarefa = self.repository.buscar_por_id(tarefa_id)
        # Tarefa de outra pessoa é tratada como "não encontrada" (não revela que existe).
        if not tarefa or tarefa.usuario_id != usuario_id:
            raise NaoEncontradoError("Tarefa não encontrada.")
        return tarefa

    # ---------- casos de uso ----------
    def criar_tarefa(self, titulo: str, usuario_id: int = 1, tipo: str = None, descricao: str = None,
                     prioridade: str = "Média", prazo=None):
        titulo, tipo, prioridade = self._validar(titulo, tipo, prioridade, prazo)
        return self.repository.criar(
            usuario_id=usuario_id,
            titulo=titulo,
            tipo=tipo,
            descricao=descricao.strip() if descricao and descricao.strip() else None,
            prioridade=prioridade,
            prazo=prazo,
        )

    def listar_tarefas(self):
        return self.repository.listar_todas()

    def listar_tarefas_do_usuario(self, usuario_id: int):
        return self.repository.listar_por_usuario(usuario_id)

    def buscar_tarefa(self, usuario_id: int, tarefa_id: int):
        return self._buscar_do_usuario(usuario_id, tarefa_id)

    def atualizar_tarefa(self, usuario_id: int, tarefa_id: int, titulo: str, tipo: str,
                         descricao: str, prioridade: str, prazo):
        titulo, tipo, prioridade = self._validar(titulo, tipo, prioridade, prazo)
        self._buscar_do_usuario(usuario_id, tarefa_id)
        return self.repository.atualizar(
            tarefa_id,
            titulo=titulo,
            tipo=tipo,
            descricao=descricao.strip() if descricao and descricao.strip() else None,
            prioridade=prioridade,
            prazo=prazo,
        )

    def alterar_conclusao(self, usuario_id: int, tarefa_id: int, concluida: bool):
        self._buscar_do_usuario(usuario_id, tarefa_id)
        return self.repository.atualizar(tarefa_id, concluida=bool(concluida))

    def excluir_tarefa(self, usuario_id: int, tarefa_id: int) -> None:
        self._buscar_do_usuario(usuario_id, tarefa_id)
        self.repository.excluir(tarefa_id)

    def excluir_concluidas(self, usuario_id: int) -> int:
        return self.repository.excluir_concluidas(usuario_id)
