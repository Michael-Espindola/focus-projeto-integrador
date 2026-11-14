"""Gera as 18 telas (9 mobile + 9 desktop) a partir de CSS/JS/HTML compartilhados.

Uso (dentro da pasta do projeto):  python tools/gerar_telas.py
Cada HTML gerado é autônomo (CSS e JS embutidos), então pode ser aberto direto no navegador.
"""
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FONTE = AQUI / "fonte"
RAIZ = AQUI.parent

BASE_CSS = (FONTE / "base.css").read_text(encoding="utf-8")
CSS = {"mobile": (FONTE / "mobile.css").read_text(encoding="utf-8"),
       "desktop": (FONTE / "desktop.css").read_text(encoding="utf-8")}
JS = (FONTE / "focus.js").read_text(encoding="utf-8")

NOMES = {  # chave -> nome do arquivo (sem sufixo/.html)
    "login": "telainicial", "identificacao": "telaIDENTIFICACAO", "cadastro": "telaCadastroNovo",
    "dashboard": "telaDashboard", "tarefas": "telaGerenciamentoTarefas", "criar": "telaCriarTarefa",
    "editar": "telaEditarTarefa", "chat": "telaChat", "usuarios": "telaUsuariosCadastrados",
}

FONTES = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
          '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
          '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">')

STATUS = '<div id="status-msg" class="status status-info" role="status" aria-live="polite"></div>'


def olho(id_alvo):
    return (f'<button type="button" class="btn-olho" data-alvo="{id_alvo}" aria-label="Mostrar senha" title="Mostrar senha">'
            '<svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>'
            '<line x1="1" y1="1" x2="23" y2="23"></line></svg></button>')


def campo_icone(id_, rotulo, icone, tipo="text", placeholder="", auto="off", com_olho=False):
    extra = " com-olho" if com_olho else ""
    return (f'<div class="campo"><label for="{id_}">{rotulo}</label><div class="com-icone">'
            f'<span class="icone" aria-hidden="true">{icone}</span>'
            f'<input type="{tipo}" id="{id_}" class="entrada{extra}" placeholder="{placeholder}" autocomplete="{auto}">'
            f'{olho(id_) if com_olho else ""}</div></div>')


# ---------------------------------------------------------------- fragmentos (iguais em mobile e desktop)
FRAG_LOGIN = f'''
<div><h1 class="titulo-tela">Bem-vindo ao FOCUS</h1><p class="subtitulo-tela">Acesse a sua conta para continuar</p></div>
<form id="form-login" novalidate>
{campo_icone("login-usuario", "E-mail ou nome de usuário", "👤", "text", "seu@email.com", "username")}
{campo_icone("senha-login", "Senha", "🔒", "password", "Digite sua senha", "current-password", True)}
<div class="linha-opcoes">
<label class="caixa-rotulo"><input type="checkbox" id="lembrar" class="caixa"> Lembrar de mim</label>
<button type="button" id="btn-esqueci" class="link-botao">Esqueceu a senha?</button>
</div>
<button type="submit" id="btn-entrar" class="btn btn-primario btn-bloco">Entrar na conta</button>
{STATUS}
</form>
<p class="texto-rodape-form">Não tem uma conta? <a class="link-botao" href="[[cadastro]]">Cadastre-se agora</a></p>
'''

FRAG_CADASTRO = f'''
<div><h1 class="titulo-tela">Criar nova conta</h1><p class="subtitulo-tela">Preencha seus dados para começar a usar o FOCUS</p></div>
<form id="form-cadastro" novalidate>
{campo_icone("nome-usuario", "Nome completo", "👤", "text", "Digite seu nome", "name")}
{campo_icone("email-usuario", "E-mail", "✉️", "email", "seu@email.com", "email")}
{campo_icone("senha-usuario", "Senha (mínimo de 6 caracteres)", "🔒", "password", "Crie uma senha", "new-password", True)}
{campo_icone("confirma-senha-usuario", "Confirmar senha", "🔒", "password", "Repita a senha", "new-password", True)}
<div class="campo"><label for="estilo-usuario">Como o Murphy (assistente) deve responder?</label>
<select id="estilo-usuario" class="selecao"><option value="direto">Direto: respostas curtas e objetivas</option><option value="detalhado">Detalhado: explicações passo a passo</option></select></div>
<button type="submit" id="btn-criar-conta" class="btn btn-primario btn-bloco">Criar conta</button>
{STATUS}
</form>
<p class="texto-rodape-form">Já tem uma conta? <a class="link-botao" href="[[login]]">Entrar</a></p>
'''


def tile(id_, rotulo, classe=""):
    return f'<div class="bloco-resumo {classe}"><strong id="{id_}">0</strong><span>{rotulo}</span></div>'


def atalho(href, icone, nome, desc):
    return (f'<a class="atalho" href="{href}"><span class="atalho-esq"><span class="atalho-icone" aria-hidden="true">{icone}</span>'
            f'<span><span class="atalho-nome">{nome}</span><span class="atalho-desc">{desc}</span></span></span>'
            '<span class="atalho-seta" aria-hidden="true">›</span></a>')


def frag_dashboard(mobile):
    usuarios = atalho("[[usuarios]]", "👥", "Usuários cadastrados", "Ver a lista oficial de usuários") if mobile else ""
    return f'''
<div><h1 class="titulo-tela">Olá, <span id="nome-usuario-logado"></span> 👋</h1><p class="subtitulo-tela">Veja como está a sua rotina hoje.</p></div>
<div class="campo pesquisa"><label class="somente-leitor" for="input-pesquisa">Pesquisar tarefa ou rotina</label>
<input type="search" id="input-pesquisa" class="entrada" placeholder="🔍 Pesquisar tarefa ou rotina..." autocomplete="off"></div>
{STATUS}
<div class="resumo" role="group" aria-label="Resumo das suas tarefas">
{tile("num-pendentes", "Pendentes")}{tile("num-concluidas", "Concluídas", "concluidas")}{tile("num-atrasadas", "Atrasadas", "atrasadas")}
</div>
<section><h2 class="titulo-secao" id="titulo-lista">Próximas tarefas</h2>
<div id="lista-proximas" class="lista-tarefas"></div>
<p style="margin-top:8px"><a id="link-ver-todas" class="link-botao" href="[[tarefas]]">Ver todas as tarefas</a></p></section>
<section><h2 class="titulo-secao">Atalhos</h2><div class="atalhos">
{atalho("[[tarefas]]", "📋", "Rotina &amp; Tarefas", "Consultar e atualizar atividades")}
{atalho("[[criar]]", "➕", "Criar Nova Tarefa", "Registrar uma nova atividade")}
{atalho("[[chat]]", "🤖", "Apoio &amp; IA Murphy", "Tirar dúvidas e organizar ideias")}
{usuarios}
</div></section>
'''


FRAG_TAREFAS = f'''
<div><h1 class="titulo-tela">Rotinas &amp; Tarefas</h1><p class="subtitulo-tela">Acompanhe, edite e conclua as suas atividades</p></div>
{STATUS}
<div class="campo pesquisa"><label class="somente-leitor" for="input-pesquisa">Pesquisar tarefa</label>
<input type="search" id="input-pesquisa" class="entrada" placeholder="🔍 Pesquisar tarefa..." autocomplete="off"></div>
<div class="filtros" role="group" aria-label="Filtrar tarefas">
<button type="button" class="filtro" data-filtro="todas" aria-pressed="true">Todas</button>
<button type="button" class="filtro" data-filtro="pendentes" aria-pressed="false">Pendentes</button>
<button type="button" class="filtro" data-filtro="concluidas" aria-pressed="false">Concluídas</button>
</div>
<div class="barra-ferramentas">
<button type="button" id="btn-atualizar" class="btn btn-primario btn-pequeno">🔄 Atualizar lista</button>
<a class="btn btn-secundario btn-pequeno" href="[[criar]]">➕ Criar tarefa</a>
<button type="button" id="btn-limpar-concluidas" class="btn btn-perigo btn-pequeno">🗑️ Limpar concluídas</button>
</div>
<div id="lista-tarefas" class="lista-tarefas"></div>
'''


def frag_form_tarefa(editando):
    titulo = "Editar Tarefa" if editando else "Criar Nova Tarefa"
    sub = "Altere os campos que desejar e salve" if editando else "Preencha os dados da sua nova atividade"
    botao = "Salvar alterações" if editando else "Salvar tarefa"
    return f'''
<div><h1 class="titulo-tela">{titulo}</h1><p class="subtitulo-tela">{sub}</p></div>
<form id="form-tarefa" novalidate>
<div class="campo"><label for="titulo-tarefa">Título da tarefa</label><input type="text" id="titulo-tarefa" class="entrada" placeholder="Ex.: Estudar FastAPI" autocomplete="off" maxlength="200"></div>
<div class="campo"><label for="tipo-tarefa">Categoria (digite livremente)</label><input type="text" id="tipo-tarefa" class="entrada" list="categorias" placeholder="Ex.: Estudos, Trabalho, Pessoal" autocomplete="off" maxlength="50">
<datalist id="categorias"><option value="Estudos"><option value="Trabalho"><option value="Pessoal"><option value="Saúde"><option value="Casa"><option value="Geral"></datalist></div>
<div class="campo"><label for="prioridade-tarefa">Prioridade</label><select id="prioridade-tarefa" class="selecao"><option value="Alta">Alta</option><option value="Média" selected>Média</option><option value="Baixa">Baixa</option></select></div>
<div class="campo"><label for="prazo-tarefa">Prazo (DD/MM/AAAA)</label><input type="text" id="prazo-tarefa" class="entrada" placeholder="DD/MM/AAAA" inputmode="numeric" autocomplete="off" maxlength="10"></div>
<div class="campo"><label for="descricao-tarefa">Descrição ou subpassos (opcional)</label><textarea id="descricao-tarefa" class="area-texto" rows="3" placeholder="Ex.: Criar os endpoints e testar" maxlength="1000"></textarea></div>
<button type="submit" id="btn-salvar-tarefa" class="btn btn-primario btn-bloco">{botao}</button>
<a class="btn btn-secundario btn-bloco" href="[[tarefas]]">Cancelar</a>
{STATUS}
</form>
'''


FRAG_USUARIOS = f'''
<div><h1 class="titulo-tela">Usuários cadastrados</h1><p class="subtitulo-tela">Lista oficial de pessoas que usam o FOCUS</p></div>
{STATUS}
<div id="lista-usuarios" class="lista-usuarios"></div>
'''

FRAG_CHAT = '''
<div id="chat-mensagens" class="chat-mensagens" aria-live="polite"></div>
<div id="sugestoes" class="sugestoes"></div>
<div class="chat-estilo"><label for="estilo-murphy">Estilo das respostas:</label>
<select id="estilo-murphy" class="selecao"><option value="direto">Direto</option><option value="detalhado">Detalhado</option></select></div>
<form id="form-chat" class="chat-entrada">
<label class="somente-leitor" for="user-input">Mensagem para o Murphy</label>
<input type="text" id="user-input" class="entrada" placeholder="Digite sua mensagem e aperte Enter..." autocomplete="off">
<button type="submit" id="send-btn" class="btn-enviar" title="Enviar" aria-label="Enviar mensagem">➤</button>
</form>
'''

# ---------------------------------------------------------------- páginas
# chave: (titulo, data-pagina, data-modo, fragmento, config mobile, nav ativo desktop, tipo desktop)
PAGINAS = {
    "login": ("FOCUS - Entrar", "login", "", FRAG_LOGIN, dict(alto=True), None, "auth"),
    "identificacao": ("FOCUS - Identificação", "login", "", FRAG_LOGIN, dict(alto=True), None, "auth"),
    "cadastro": ("FOCUS - Criar conta", "cadastro", "", FRAG_CADASTRO, dict(voltar="login"), None, "auth"),
    "dashboard": ("FOCUS - Painel principal", "dashboard", "", None, dict(sair=True), "dashboard", "app"),
    "tarefas": ("FOCUS - Rotinas e Tarefas", "tarefas", "", FRAG_TAREFAS, dict(voltar="dashboard", sair=True), "tarefas", "app"),
    "criar": ("FOCUS - Criar tarefa", "formTarefa", "criar", None, dict(voltar="tarefas"), "criar", "app"),
    "editar": ("FOCUS - Editar tarefa", "formTarefa", "editar", None, dict(voltar="tarefas"), "tarefas", "app"),
    "usuarios": ("FOCUS - Usuários cadastrados", "usuarios", "", FRAG_USUARIOS, dict(voltar="dashboard"), "usuarios", "app"),
    "chat": ("FOCUS - Murphy IA", "chat", "", FRAG_CHAT, {}, "chat", "chat"),
}

NAV = [("dashboard", "📊", "Dashboard"), ("tarefas", "📋", "Rotinas &amp; Tarefas"), ("criar", "➕", "Criar Tarefa"),
       ("chat", "🤖", "Murphy IA"), ("usuarios", "👥", "Usuários cadastrados")]


def fragmento(chave, frag, mobile):
    if chave == "dashboard":
        return frag_dashboard(mobile)
    if chave == "criar":
        return frag_form_tarefa(False)
    if chave == "editar":
        return frag_form_tarefa(True)
    return frag


def casca_mobile(chave, titulo, pagina, modo, frag, cfg):
    if chave == "chat":
        corpo = ('<div class="chat-topo"><div class="chat-topo-info">'
                 '<a class="btn-topo redondo" href="[[dashboard]]" aria-label="Voltar ao painel" title="Voltar">←</a>'
                 '<div><div class="chat-titulo">Murphy IA 🤖</div><div class="chat-subtitulo">Seu assistente inteligente</div></div></div>'
                 '<button type="button" id="clear-btn" class="btn-topo redondo" title="Apagar a conversa" aria-label="Apagar a conversa">🗑️</button></div>'
                 + frag)
    else:
        esq = (f'<a class="btn-topo redondo" href="[[{cfg["voltar"]}]]" aria-label="Voltar" title="Voltar">←</a>'
               if cfg.get("voltar") else "<span></span>")
        dir_ = ('<button type="button" class="btn-topo" data-acao="sair">Sair 🚪</button>' if cfg.get("sair") else "<span></span>")
        banner = (f'<header class="banner{" alto" if cfg.get("alto") else ""}"><div class="banner-topo">{esq}{dir_}</div>'
                  '<div class="banner-marca"><div class="logo" aria-hidden="true">F</div></div></header>')
        centro = " centro" if chave in ("login", "identificacao") else ""
        corpo = (banner + f'<main class="conteudo{centro}">{frag}</main>'
                 '<footer class="rodape">FOCUS • Organização pessoal</footer>')
    return f'<div class="app">{corpo}</div>'


def casca_desktop(chave, titulo, pagina, modo, frag, ativo, tipo):
    if tipo == "auth":
        painel = ('<aside class="painel-marca"><div class="logo" aria-hidden="true">F</div><h1>FOCUS</h1>'
                  '<p>Assistente de organização e foco</p></aside>')
        return (f'<div class="app">{painel}<main class="conteudo-desktop centralizado"><div class="coluna estreita">{frag}</div></main></div>')
    links = ""
    for k, ic, nome in NAV:
        atual = k == ativo
        classe = "nav-link ativo" if atual else "nav-link"
        aria = ' aria-current="page"' if atual else ""
        links += f'<a class="{classe}" href="[[{k}]]"{aria}>{ic} {nome}</a>'

    menu = ('<nav class="menu-lateral" aria-label="Menu principal"><div><div class="menu-marca"><div class="logo" aria-hidden="true">F</div>'
            f'<span class="menu-nome">FOCUS</span></div><div class="menu-nav">{links}</div></div>'
            '<div class="menu-rodape"><div id="menu-usuario" class="menu-usuario"></div>'
            '<button type="button" class="nav-link" data-acao="sair">🚪 Sair da conta</button></div></nav>')
    if tipo == "chat":
        topo = ('<div class="chat-topo"><div><div class="chat-titulo">Murphy IA 🤖</div>'
                '<div class="chat-subtitulo">Assistente pessoal inteligente, amigável e conversacional</div></div>'
                '<button type="button" id="clear-btn" class="btn btn-secundario">🗑️ Nova conversa</button></div>')
        return f'<div class="app">{menu}<section class="area-chat">{topo}{frag}</section></div>'
    return f'<div class="app">{menu}<main class="conteudo-desktop"><div class="coluna">{frag}</div></main></div>'


def montar(plataforma, chave):
    titulo, pagina, modo, frag, cfg, ativo, tipo = PAGINAS[chave]
    mobile = plataforma == "mobile"
    sufixo = "" if mobile else "Desktop"
    frag = fragmento(chave, frag, mobile)
    corpo = (casca_mobile(chave, titulo, pagina, modo, frag, cfg) if mobile
             else casca_desktop(chave, titulo, pagina, modo, frag, ativo, tipo))
    for k, nome in NOMES.items():
        corpo = corpo.replace(f"[[{k}]]", f"{nome}{sufixo}.html")
    suf_titulo = "" if mobile else " (Desktop)"
    attr_modo = f' data-modo="{modo}"' if modo else ""
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo}{suf_titulo}</title>
{FONTES}
<style>
{BASE_CSS}
{CSS[plataforma]}
</style>
</head>
<body class="{plataforma}" data-pagina="{pagina}"{attr_modo}>
{corpo}
<script>
{JS}
</script>
</body>
</html>
'''


def main():
    total = 0
    for plataforma, pasta in (("mobile", "telas_mobile"), ("desktop", "telas_desktop")):
        destino = RAIZ / pasta
        destino.mkdir(exist_ok=True)
        for chave in PAGINAS:
            sufixo = "" if plataforma == "mobile" else "Desktop"
            arquivo = destino / f"{NOMES[chave]}{sufixo}.html"
            arquivo.write_text(montar(plataforma, chave), encoding="utf-8")
            total += 1
    print(f"{total} telas geradas.")


if __name__ == "__main__":
    main()
