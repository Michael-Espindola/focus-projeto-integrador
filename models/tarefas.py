from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from config.database import Base


class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, nullable=False)
    tipo = Column(String(50))
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text)
    prioridade = Column(String(20))
    prazo = Column(Date)
    concluida = Column(Boolean, default=False)
    criado_em = Column(DateTime, server_default=func.now())
