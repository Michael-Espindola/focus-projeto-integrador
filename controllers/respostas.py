"""Padroniza as respostas dos controllers: sempre um dicionário com 'sucesso', 'tipo' e 'mensagem'."""
from services.excecoes import NaoEncontradoError


def sucesso(mensagem: str, dados=None) -> dict:
    resposta = {"sucesso": True, "tipo": "SUCESSO", "mensagem": mensagem}
    if dados is not None:
        resposta["dados"] = dados
    return resposta


def falha(tipo: str, mensagem: str) -> dict:
    return {"sucesso": False, "tipo": tipo, "mensagem": mensagem}


def executar(operacao, mensagem_sucesso: str, mensagem_falha: str) -> dict:
    """Roda a operação e traduz as exceções em respostas padronizadas."""
    try:
        return sucesso(mensagem_sucesso, operacao())
    except NaoEncontradoError as erro:
        return falha("NAO_ENCONTRADO", str(erro))
    except ValueError as erro:
        return falha("REGRA_NEGOCIO", str(erro))
    except Exception as erro:
        print("ERRO TÉCNICO:", erro)
        return falha("FALHA_TECNICA", mensagem_falha)
