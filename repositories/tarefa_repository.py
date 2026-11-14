from sqlalchemy import delete, select

from config.database import SessionLocal
from models.tarefas import Tarefa


class TarefaRepository:
    """Único lugar que conversa com a tabela 'tarefas'."""

    def listar_todas(self):
        with SessionLocal() as session:
            return list(session.scalars(select(Tarefa)).all())

    def listar_por_usuario(self, usuario_id: int):
        with SessionLocal() as session:
            comando = select(Tarefa).where(Tarefa.usuario_id == usuario_id).order_by(Tarefa.id.asc())
            return list(session.scalars(comando).all())

    def buscar_por_id(self, id_tarefa: int):
        with SessionLocal() as session:
            return session.scalar(select(Tarefa).where(Tarefa.id == id_tarefa))

    def criar(self, usuario_id: int, titulo: str, tipo: str = None, descricao: str = None,
              prioridade: str = "Média", prazo=None):
        with SessionLocal() as session:
            nova = Tarefa(
                usuario_id=usuario_id, titulo=titulo, tipo=tipo,
                descricao=descricao, prioridade=prioridade, prazo=prazo,
            )
            session.add(nova)
            session.commit()
            session.refresh(nova)
            return nova

    def atualizar(self, id_tarefa: int, **campos):
        """Atualiza só os campos informados. Retorna a tarefa ou None se não existir."""
        with SessionLocal() as session:
            tarefa = session.get(Tarefa, id_tarefa)
            if not tarefa:
                return None
            for nome, valor in campos.items():
                setattr(tarefa, nome, valor)
            session.commit()
            session.refresh(tarefa)
            return tarefa

    def excluir(self, id_tarefa: int) -> bool:
        with SessionLocal() as session:
            tarefa = session.get(Tarefa, id_tarefa)
            if not tarefa:
                return False
            session.delete(tarefa)
            session.commit()
            return True

    def excluir_concluidas(self, usuario_id: int) -> int:
        with SessionLocal() as session:
            resultado = session.execute(
                delete(Tarefa).where(Tarefa.usuario_id == usuario_id, Tarefa.concluida.is_(True))
            )
            session.commit()
            return resultado.rowcount or 0
