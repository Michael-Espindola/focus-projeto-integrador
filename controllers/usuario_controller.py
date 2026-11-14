from controllers.respostas import executar, falha, sucesso
from services.usuario_service import ESTILOS_VALIDOS, UsuarioService


def usuario_para_dict(u) -> dict:
    """Nunca inclui a senha."""
    return {
        "id": u.id,
        "nome": u.nome,
        "email": u.email,
        "estilo_instrucao": u.estilo_instrucao,
        "papel": u.papel,
    }


class UsuarioController:

    def __init__(self, service=None):
        self.service = service or UsuarioService()

    def listar_usuarios(self):
        return executar(
            lambda: [usuario_para_dict(u) for u in self.service.listar_usuarios()],
            "Usuários listados com sucesso!",
            "Não foi possível carregar os usuários.",
        )

    def listar_perfis(self):
        """Só os nomes (mantido por compatibilidade)."""
        try:
            return [u.nome for u in self.service.listar_usuarios()]
        except Exception as erro:
            print("ERRO TÉCNICO AO LISTAR PERFIS:", erro)
            return []

    def buscar_por_id(self, usuario_id: int):
        try:
            usuario = self.service.buscar_por_id(usuario_id)
            return usuario_para_dict(usuario) if usuario else None
        except Exception:
            return None

    def criar_perfil(self, nome, email, senha, estilo_instrucao="direto"):
        if estilo_instrucao not in ESTILOS_VALIDOS:
            return falha("REGRA_NEGOCIO", "Estilo inválido. Escolha exatamente 'direto' ou 'detalhado'.")
        # O papel NUNCA vem do cliente: todo cadastro público é 'usuario'.
        return executar(
            lambda: usuario_para_dict(self.service.criar_usuario(
                nome=nome, email=email, senha=senha, estilo_instrucao=estilo_instrucao, papel="usuario")),
            "Conta criada com sucesso!",
            "Não foi possível criar a conta. Tente novamente.",
        )

    def criar(self, nome, email, senha, estilo_instrucao="direto"):
        return self.criar_perfil(nome, email, senha, estilo_instrucao)

    def autenticar_usuario(self, identificador: str, senha: str):
        def operacao():
            resultado = self.service.autenticar_usuario(identificador, senha)
            dados = usuario_para_dict(resultado["usuario"])
            dados["access_token"] = resultado["access_token"]
            dados["token_type"] = resultado["token_type"]
            return dados

        resposta = executar(operacao, "Login efetuado com sucesso!",
                            "Erro técnico ao tentar efetuar login.")
        if not resposta["sucesso"] and resposta["tipo"] == "REGRA_NEGOCIO":
            resposta["tipo"] = "NAO_AUTORIZADO"  # vira HTTP 401
        return resposta

    def atualizar_estilo(self, usuario_id: int, estilo_instrucao: str):
        return executar(
            lambda: usuario_para_dict(self.service.atualizar_estilo(usuario_id, estilo_instrucao)),
            "Estilo atualizado com sucesso!",
            "Não foi possível atualizar o perfil.",
        )

    def atualizar_perfil(self, nome, estilo_instrucao):
        return executar(
            lambda: usuario_para_dict(self.service.atualizar_usuario(nome, estilo_instrucao)),
            "Perfil atualizado.",
            "Não foi possível atualizar o perfil.",
        )

    def excluir_perfil(self, usuario_id):
        try:
            resposta = self.service.excluir_usuario(usuario_id)
        except Exception as erro:
            print("ERRO TÉCNICO:", erro)
            return falha("FALHA_TECNICA", "Não foi possível excluir o usuário.")
        if not resposta.get("sucesso", True):
            mensagem = resposta.get("mensagem", "Erro ao excluir.")
            tipo = "NAO_ENCONTRADO" if "não encontrado" in mensagem.lower() else "REGRA_NEGOCIO"
            return falha(tipo, mensagem)
        return sucesso(resposta.get("mensagem", "Usuário excluído com sucesso."))
