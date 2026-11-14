"""Murphy: assistente de IA do FOCUS (Google Gemini).

Teste rápido pelo terminal:  python services/chatbot.py
"""
import os
import sys
import time
from datetime import date

from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":  # permite rodar este arquivo direto, fora do uvicorn
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from repositories.tarefa_repository import TarefaRepository  # noqa: E402


class IAIndisponivelError(Exception):
    """A IA não respondeu (sem chave, sem internet, cota esgotada, etc.)."""


# Modelo principal vem do .env (GEMINI_MODEL); se falhar, tenta os próximos da lista.
_MODELOS_BRUTOS = [
    os.getenv("GEMINI_MODEL", ""),
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash",
]
MODELOS_GEMINI = list(dict.fromkeys(m for m in _MODELOS_BRUTOS if m))

COOLDOWN_SEGUNDOS = 120   # modelo que falhou fica "de castigo" por um tempo
TIMEOUT_MS = int(os.getenv("GEMINI_TIMEOUT_MS") or 25000)
_modelos_em_castigo = {}  # modelo -> até quando evitar
_ultimo_modelo_ok = None
_cliente = None


def _obter_cliente():
    global _cliente
    if _cliente is not None:
        return _cliente
    chave = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not chave:
        raise IAIndisponivelError("A chave GEMINI_API_KEY não foi encontrada no arquivo .env.")
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise IAIndisponivelError("A biblioteca google-genai não está instalada. Rode: pip install -r requirements.txt")
    _cliente = genai.Client(api_key=chave, http_options=types.HttpOptions(timeout=TIMEOUT_MS))
    return _cliente


def _ordem_dos_modelos():
    agora = time.time()
    bons = [m for m in MODELOS_GEMINI if _modelos_em_castigo.get(m, 0) <= agora]
    ruins = [m for m in MODELOS_GEMINI if m not in bons]
    if _ultimo_modelo_ok in bons:
        bons.remove(_ultimo_modelo_ok)
        bons.insert(0, _ultimo_modelo_ok)
    return bons + ruins


def _gerar(itens, instrucao: str) -> str:
    """itens = lista de (papel, texto), papel 'user' ou 'model'. Tenta cada modelo até um responder."""
    global _ultimo_modelo_ok
    from google.genai import types

    cliente = _obter_cliente()
    conteudo = [types.Content(role=p, parts=[types.Part(text=t)]) for p, t in itens]
    ultimo_erro = None

    for modelo in _ordem_dos_modelos():
        inicio = time.time()
        try:
            resposta = cliente.models.generate_content(
                model=modelo,
                contents=conteudo,
                config=types.GenerateContentConfig(system_instruction=instrucao, max_output_tokens=2048),
            )
            texto = (resposta.text or "").strip() if resposta else ""
            if texto:
                _ultimo_modelo_ok = modelo
                _modelos_em_castigo.pop(modelo, None)
                print(f"[Murphy] OK com {modelo} em {time.time() - inicio:.1f}s")
                return texto
            ultimo_erro = f"{modelo}: resposta vazia"
        except Exception as erro:
            ultimo_erro = f"{modelo}: {erro}"
            _modelos_em_castigo[modelo] = time.time() + COOLDOWN_SEGUNDOS
            print(f"[Murphy] Falha no modelo {modelo} após {time.time() - inicio:.1f}s: {erro}")

    print(f"[Murphy] Todos os modelos falharam. Último erro: {ultimo_erro}")
    raise IAIndisponivelError(
        "Não consegui falar com a IA agora. Verifique a chave GEMINI_API_KEY e a conexão com a internet."
    )


def carregar_tarefas_texto(usuario_id) -> str:
    """Resume as tarefas do usuário para o Murphy usar como contexto."""
    if not usuario_id:
        return "Nenhuma tarefa cadastrada no momento."
    try:
        tarefas = TarefaRepository().listar_por_usuario(usuario_id)
    except Exception as erro:
        print(f"Aviso: não foi possível carregar as tarefas para o Murphy: {erro}")
        return "Nenhuma tarefa cadastrada no momento."
    if not tarefas:
        return "Nenhuma tarefa cadastrada no momento."

    # Pendentes primeiro, por prazo; limita a 30 para não estourar o contexto.
    tarefas.sort(key=lambda t: (bool(t.concluida), t.prazo or date.max))
    linhas = []
    for t in tarefas[:30]:
        situacao = "concluída" if t.concluida else "pendente"
        prazo = t.prazo.strftime("%d/%m/%Y") if t.prazo else "sem prazo"
        linha = f"- {t.titulo} | categoria: {t.tipo} | prioridade: {t.prioridade} | prazo: {prazo} | {situacao}"
        if t.descricao:
            linha += f" | detalhes: {t.descricao}"
        linhas.append(linha)
    return "\n".join(linhas)


def montar_instrucao(nome, estilo, tarefas_txt) -> str:
    hoje = date.today().strftime("%d/%m/%Y")
    guia_estilo = (
        "Seja direto: respostas curtas, objetivas, sem enrolação."
        if estilo == "direto"
        else "Seja detalhado: explique o raciocínio, dê passos claros e exemplos quando ajudar."
    )
    return f"""Você é o Murphy, assistente pessoal do aplicativo FOCUS (organização de rotina e tarefas).
Você está conversando com {nome or "o usuário"}. Hoje é {hoje}.

Como conversar:
- Responda SEMPRE em português do Brasil, com tom natural, amigável e humano, como um bom amigo mentor.
- Leia o que a pessoa realmente quis dizer e responda exatamente a isso. Cumprimento recebe cumprimento; dúvida recebe resposta; desabafo recebe acolhimento antes de qualquer conselho.
- Use o histórico da conversa: lembre do que já foi dito e não repita perguntas ou apresentações.
- Se o pedido for vago, faça UMA pergunta curta para esclarecer. Não faça várias perguntas de uma vez.
- Nunca use frases engessadas nem repita a mesma resposta. Varie.
- Estilo preferido do usuário: {guia_estilo}
- Pode usar formatação simples (listas com "-", **negrito**) quando ajudar. Evite títulos grandes e use poucos emojis.
- Você pode conversar sobre qualquer assunto, não só sobre tarefas.

Sobre as tarefas do usuário no FOCUS (use só quando for relevante, nunca invente tarefas que não estão aqui):
{tarefas_txt}

Você não cria nem altera tarefas diretamente. Quando fizer sentido, sugira que ele crie a tarefa na tela "Criar Tarefa", indicando título, categoria, prioridade e prazo sugeridos.
Ao priorizar, considere prazo próximo, prioridade alta e tarefas pendentes."""


def _montar_itens(comando: str, historico) -> list:
    itens = []
    for m in (historico or [])[-20:]:
        papel = "model" if m.get("papel") in ("model", "ai", "assistant", "murphy") else "user"
        texto = (m.get("texto") or "").strip()
        if texto:
            itens.append((papel, texto))
    while itens and itens[0][0] != "user":  # o histórico precisa começar com o usuário
        itens.pop(0)
    itens.append(("user", comando.strip()))
    return itens


def perguntar_ao_murphy(comando: str, nome_usuario: str = None, estilo: str = "direto",
                        historico=None, usuario_id=None) -> str:
    """Devolve a resposta do Murphy. Levanta IAIndisponivelError se a IA não responder."""
    instrucao = montar_instrucao(nome_usuario, estilo, carregar_tarefas_texto(usuario_id))
    return _gerar(_montar_itens(comando, historico), instrucao)


def desmembrar_tarefa_ia(titulo_tarefa: str) -> list:
    """Quebra uma tarefa em 3 a 4 passos curtos."""
    instrucao = "Você é o Murphy, assistente do FOCUS. Responda em português do Brasil."
    pedido = f"Desmembre a tarefa '{titulo_tarefa}' em 3 a 4 passos práticos e curtos, em lista simples."
    texto = _gerar([("user", pedido)], instrucao)
    return [p.strip(" -*•") for p in texto.split("\n") if p.strip()]


if __name__ == "__main__":
    try:
        print(perguntar_ao_murphy("Oi! Quem é você?", nome_usuario="Teste"))
    except IAIndisponivelError as erro:
        print("Murphy indisponível:", erro)
