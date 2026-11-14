import re

from config.seguranca import criar_token, gerar_hash_senha, senha_tem_hash, verificar_senha
from repositories.usuario_repository import UsuarioRepository

_REGEX_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
ESTILOS_VALIDOS = ("direto", "detalhado")


class UsuarioService:
    """Regras de negócio dos usuários e do login."""

    def __init__(self, repository=None):
        self.repository = repository or UsuarioRepository()

    def listar_usuarios(self):
        return self.repository.listar_todos()

    def buscar_por_id(self, usuario_id: int):
        return self.repository.buscar_por_id(usuario_id)

    def criar_usuario(self, nome: str, email: str, senha: str, estilo_instrucao: str = "direto",
                      papel: str = "usuario"):
        if not nome or not nome.strip():
            raise ValueError("O nome do usuário não pode ficar em branco.")
        if len(nome.strip()) < 2:
            raise ValueError("O nome do usuário deve ter pelo menos 2 caracteres.")
        if "@" in nome:
            raise ValueError("O nome do usuário não pode conter o caractere @.")

        if not email or not email.strip() or not _REGEX_EMAIL.match(email.strip()):
            raise ValueError("O e-mail informado é inválido ou está em branco.")

        if not senha or not senha.strip():
            raise ValueError("A senha não pode ficar em branco.")
        if len(senha.strip()) < 6:
            raise ValueError("A senha deve ter pelo menos 6 caracteres.")

        if not estilo_instrucao or estilo_instrucao.strip() not in ESTILOS_VALIDOS:
            raise ValueError("O estilo de instrução deve ser exatamente 'direto' ou 'detalhado'.")

        if self.repository.buscar_por_nome(nome.strip()):
            raise ValueError(f"Já existe um usuário com o nome '{nome.strip()}' cadastrado.")
        if self.repository.buscar_por_nome_ou_email(email.strip()):
            raise ValueError(f"Já existe um usuário com o e-mail '{email.strip()}' cadastrado.")

        return self.repository.criar(
            nome=nome.strip(),
            email=email.strip().lower(),
            senha=gerar_hash_senha(senha.strip()),
            estilo_instrucao=estilo_instrucao.strip(),
            papel=papel,
        )

    def autenticar_usuario(self, identificador: str, senha: str):
        if not identificador or not identificador.strip() or not senha or not senha.strip():
            raise ValueError("Preencha o usuário (ou e-mail) e a senha.")

        usuario = self.repository.buscar_por_nome_ou_email(identificador.strip())
        # Mesma mensagem para "usuário inexistente" e "senha errada" (não revela qual dos dois).
        if not usuario or not verificar_senha(senha.strip(), usuario.senha):
            raise ValueError("Usuário/e-mail ou senha incorretos.")

        # Contas antigas (senha em texto puro) são convertidas para hash no primeiro login.
        if not senha_tem_hash(usuario.senha):
            try:
                self.repository.atualizar_senha(usuario.id, gerar_hash_senha(senha.strip()))
            except Exception as erro:
                print("Aviso: não foi possível converter a senha antiga em hash:", erro)

        return {"access_token": criar_token(usuario), "token_type": "bearer", "usuario": usuario}

    def atualizar_usuario(self, nome: str, estilo_instrucao: str):
        usuario = self.repository.buscar_por_nome(nome)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        return self.atualizar_estilo(usuario.id, estilo_instrucao)

    def atualizar_estilo(self, usuario_id: int, estilo_instrucao: str):
        if estilo_instrucao not in ESTILOS_VALIDOS:
            raise ValueError("Estilo inválido. Escolha exatamente 'direto' ou 'detalhado'.")
        usuario = self.repository.atualizar(usuario_id, estilo_instrucao)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        return usuario

    def excluir_usuario(self, usuario_id: int):
        if not self.buscar_por_id(usuario_id):
            return {"sucesso": False, "mensagem": "Usuário não encontrado."}
        if self.repository.excluir(usuario_id):
            return {"sucesso": True, "mensagem": "Usuário excluído com sucesso."}
        return {"sucesso": False, "mensagem": "Não foi possível excluir o usuário."}
