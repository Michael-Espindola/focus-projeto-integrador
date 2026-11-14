from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from config.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False, unique=True)
    email = Column(String(150), nullable=True, unique=True)  # login por nome OU e-mail
    senha = Column(String(255), nullable=False)  # guarda o HASH da senha, nunca o texto puro
    estilo_instrucao = Column(String(20), nullable=False, default="direto")
    papel = Column(String(20), nullable=False, default="usuario")
    criado_em = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return (
            f"Usuario(id={self.id}, nome='{self.nome}', email='{self.email}', "
            f"estilo='{self.estilo_instrucao}', papel='{self.papel}')"
        )
