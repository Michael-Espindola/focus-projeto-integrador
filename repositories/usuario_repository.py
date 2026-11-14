from sqlalchemy import delete, func, or_, select

from config.database import SessionLocal
from models.tarefas import Tarefa
from models.usuario import Usuario


class UsuarioRepository:
    """Único lugar que conversa com a tabela 'usuarios'."""

    def listar_todos(self):
        with SessionLocal() as session:
            return list(session.scalars(select(Usuario).order_by(Usuario.nome)).all())

    def buscar_por_id(self, usuario_id: int):
        with SessionLocal() as session:
            return session.scalar(select(Usuario).where(Usuario.id == usuario_id))

    def buscar_por_nome(self, nome: str):
        with SessionLocal() as session:
            comando = select(Usuario).where(func.lower(Usuario.nome) == nome.lower())
            return session.scalar(comando)

    def buscar_por_nome_ou_email(self, identificador: str):
        """Usado no login e na checagem de e-mail repetido (ignora maiúsculas/minúsculas)."""
        with SessionLocal() as session:
            termo = identificador.lower()
            comando = select(Usuario).where(
                or_(func.lower(Usuario.nome) == termo, func.lower(Usuario.email) == termo)
            )
            return session.scalar(comando)

    def criar(self, nome: str, email: str = None, senha: str = "", estilo_instrucao: str = "direto",
              papel: str = "usuario"):
        with SessionLocal() as session:
            novo = Usuario(nome=nome, email=email, senha=senha,
                           estilo_instrucao=estilo_instrucao, papel=papel)
            session.add(novo)
            session.commit()
            session.refresh(novo)
            return novo

    def atualizar(self, usuario_id: int, estilo_instrucao: str):
        with SessionLocal() as session:
            usuario = session.get(Usuario, usuario_id)
            if usuario:
                usuario.estilo_instrucao = estilo_instrucao
                session.commit()
                session.refresh(usuario)
            return usuario

    def atualizar_senha(self, usuario_id: int, senha_hash: str) -> None:
        with SessionLocal() as session:
            usuario = session.get(Usuario, usuario_id)
            if usuario:
                usuario.senha = senha_hash
                session.commit()

    def excluir(self, usuario_id: int) -> bool:
        """Exclui o usuário e as tarefas dele (para não sobrar tarefa 'órfã')."""
        with SessionLocal() as session:
            usuario = session.get(Usuario, usuario_id)
            if not usuario:
                return False
            session.execute(delete(Tarefa).where(Tarefa.usuario_id == usuario_id))
            session.delete(usuario)
            session.commit()
            return True
