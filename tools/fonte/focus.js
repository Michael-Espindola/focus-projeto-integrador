/* FOCUS - lógica compartilhada das telas (mobile e desktop) */
(function () {
  'use strict';

  var SUFIXO = document.body.classList.contains('desktop') ? 'Desktop' : '';
  var PAGINAS = {
    login: 'telainicial' + SUFIXO + '.html',
    cadastro: 'telaCadastroNovo' + SUFIXO + '.html',
    dashboard: 'telaDashboard' + SUFIXO + '.html',
    tarefas: 'telaGerenciamentoTarefas' + SUFIXO + '.html',
    criar: 'telaCriarTarefa' + SUFIXO + '.html',
    editar: 'telaEditarTarefa' + SUFIXO + '.html',
    chat: 'telaChat' + SUFIXO + '.html',
    usuarios: 'telaUsuariosCadastrados' + SUFIXO + '.html'
  };

  // Se a tela vier de um servidor HTTP/HTTPS (local ou Render), usa a mesma origem;
  // se for aberta diretamente pelo disco (file://), aponta para o servidor local.
  var API = (location.protocol === 'http:' || location.protocol === 'https:')
    ? location.origin : 'http://127.0.0.1:8000';

  var CHAVE_SESSAO = 'focus_sessao';
  var CHAVE_AVISO = 'focus_aviso';

  function $(seletor, raiz) { return (raiz || document).querySelector(seletor); }
  function $$(seletor, raiz) { return Array.prototype.slice.call((raiz || document).querySelectorAll(seletor)); }

  function esc(texto) {
    return String(texto == null ? '' : texto)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  /* ---------- Sessão (token + dados do usuário) ---------- */
  function lerSessao() {
    var armazens = [window.sessionStorage, window.localStorage];
    for (var i = 0; i < armazens.length; i++) {
      try {
        var bruto = armazens[i].getItem(CHAVE_SESSAO);
        if (bruto) { var s = JSON.parse(bruto); if (s && s.token) return s; }
      } catch (e) { /* ignora */ }
    }
    return null;
  }
  function limparSessao() {
    try { window.sessionStorage.removeItem(CHAVE_SESSAO); } catch (e) {}
    try { window.localStorage.removeItem(CHAVE_SESSAO); } catch (e) {}
  }
  function salvarSessao(dados, lembrar) {
    limparSessao();
    try { (lembrar ? window.localStorage : window.sessionStorage).setItem(CHAVE_SESSAO, JSON.stringify(dados)); } catch (e) {}
  }
  function atualizarSessao(parcial) {
    var s = lerSessao(); if (!s) return;
    var noLocal = false;
    try { noLocal = !!window.localStorage.getItem(CHAVE_SESSAO); } catch (e) {}
    for (var k in parcial) { if (Object.prototype.hasOwnProperty.call(parcial, k)) s[k] = parcial[k]; }
    salvarSessao(s, noLocal);
  }
  function guardarAviso(texto) { try { window.sessionStorage.setItem(CHAVE_AVISO, texto); } catch (e) {} }
  function lerAviso() {
    try { var a = window.sessionStorage.getItem(CHAVE_AVISO); window.sessionStorage.removeItem(CHAVE_AVISO); return a; } catch (e) { return null; }
  }
  function irPara(chave, consulta) { window.location.href = PAGINAS[chave] + (consulta || ''); }

  function exigirLogin() {
    var s = lerSessao();
    if (!s) { guardarAviso('Faça login para continuar.'); window.location.replace(PAGINAS.login); return null; }
    return s;
  }

  function primeiroNome(nome) {
    var p = String(nome || '').trim().split(/\s+/)[0] || '';
    return p ? p.charAt(0).toUpperCase() + p.slice(1) : '';
  }

  /* ---------- Chamadas à API ---------- */
  function extrairErro(data, status) {
    if (data && typeof data.detail === 'string' && data.detail) return data.detail;
    if (data && Array.isArray(data.detail) && data.detail.length) {
      return data.detail.map(function (d) { return d.msg || ''; }).filter(Boolean).join(' ');
    }
    if (status === 401) return 'Sua sessão expirou. Faça login novamente.';
    if (status === 403) return 'Você não tem permissão para esta ação.';
    if (status === 404) return 'Item não encontrado.';
    if (status >= 500) return 'Erro interno no servidor. Tente novamente em instantes.';
    return 'Não foi possível concluir a operação.';
  }

  function api(caminho, opcoes) {
    opcoes = opcoes || {};
    var cab = {};
    var sessao = lerSessao();
    var comAuth = opcoes.auth !== false;
    if (comAuth && sessao) cab['Authorization'] = 'Bearer ' + sessao.token;
    var corpo;
    if (opcoes.form) { corpo = new URLSearchParams(opcoes.form); }
    else if (opcoes.corpo !== undefined) { cab['Content-Type'] = 'application/json'; corpo = JSON.stringify(opcoes.corpo); }

    return fetch(API + caminho, { method: opcoes.metodo || 'GET', headers: cab, body: corpo })
      .then(function (resp) {
        return resp.json().catch(function () { return {}; }).then(function (data) {
          if (resp.status === 401 && comAuth) {
            limparSessao();
            guardarAviso(extrairErro(data, 401));
            window.location.replace(PAGINAS.login);
          }
          return { ok: resp.ok, status: resp.status, data: data, erro: resp.ok ? null : extrairErro(data, resp.status) };
        });
      })
      .catch(function () {
        return { ok: false, status: 0, data: {}, erro: 'Não foi possível conectar ao servidor. Verifique se o sistema está ligado e tente novamente.' };
      });
  }

  /* ---------- Mensagens e validação ---------- */
  function mostrar(el, tipo, texto) {
    if (!el) return;
    el.className = 'status status-' + tipo + (el.dataset.centro ? ' status-centro' : '');
    el.textContent = texto || '';
  }

  function erroCampo(input, mensagem) {
    var id = 'erro-' + input.id;
    var el = document.getElementById(id);
    if (!el) {
      el = document.createElement('small');
      el.id = id; el.className = 'erro-campo'; el.setAttribute('role', 'alert');
      var grupo = input.closest('.campo') || input.parentNode;
      grupo.appendChild(el);
    }
    el.textContent = mensagem || '';
    if (mensagem) { input.setAttribute('aria-invalid', 'true'); input.setAttribute('aria-describedby', id); }
    else { input.removeAttribute('aria-invalid'); input.removeAttribute('aria-describedby'); }
    return !mensagem;
  }

  function limparErrosAoDigitar(campos) {
    campos.forEach(function (c) {
      if (!c) return;
      var evento = c.tagName === 'SELECT' ? 'change' : 'input';
      c.addEventListener(evento, function () { erroCampo(c, ''); });
    });
  }

  function focarPrimeiroErro(campos) {
    for (var i = 0; i < campos.length; i++) {
      if (campos[i] && campos[i].getAttribute('aria-invalid') === 'true') { campos[i].focus(); return; }
    }
  }

  var REGEX_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  /* ---------- Datas ---------- */
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function hojeISO() { var h = new Date(); return h.getFullYear() + '-' + pad(h.getMonth() + 1) + '-' + pad(h.getDate()); }
  function hojeBR() { var h = new Date(); return pad(h.getDate()) + '/' + pad(h.getMonth() + 1) + '/' + h.getFullYear(); }
  function isoParaBR(iso) {
    var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || '');
    return m ? m[3] + '/' + m[2] + '/' + m[1] : '';
  }
  function brParaISO(br) {
    var m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec((br || '').trim());
    if (!m) return null;
    var d = +m[1], mes = +m[2], a = +m[3];
    if (a < 2000 || a > 2100) return null;
    var dt = new Date(a, mes - 1, d);
    if (dt.getFullYear() !== a || dt.getMonth() !== mes - 1 || dt.getDate() !== d) return null;
    return m[3] + '-' + m[2] + '-' + m[1];
  }
  function mascaraData(input) {
    input.addEventListener('input', function () {
      var v = input.value.replace(/\D/g, '').slice(0, 8);
      if (v.length > 4) v = v.replace(/^(\d{2})(\d{2})(\d{0,4})/, '$1/$2/$3');
      else if (v.length > 2) v = v.replace(/^(\d{2})(\d{0,2})/, '$1/$2');
      input.value = v;
    });
  }
  function estaAtrasada(t) { return !t.concluida && !!t.prazo && t.prazo < hojeISO(); }
  function classePrioridade(p) {
    var x = String(p || '').toLowerCase();
    if (x.indexOf('alt') === 0) return 'alta';
    if (x.indexOf('baix') === 0) return 'baixa';
    return 'media';
  }
  function ordenarTarefas(lista) {
    return lista.slice().sort(function (a, b) {
      if (!!a.concluida !== !!b.concluida) return a.concluida ? 1 : -1;
      var pa = a.prazo || '9999-99-99', pb = b.prazo || '9999-99-99';
      if (pa !== pb) return pa < pb ? -1 : 1;
      return a.id - b.id;
    });
  }

  /* ---------- Componentes ---------- */
  function iniciarOlhos() {
    $$('.btn-olho').forEach(function (btn) {
      var campo = document.getElementById(btn.getAttribute('data-alvo'));
      var icone = btn.querySelector('svg');
      var FECHADO = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
      var ABERTO = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
      btn.addEventListener('click', function () {
        var mostrando = campo.type === 'text';
        campo.type = mostrando ? 'password' : 'text';
        icone.innerHTML = mostrando ? FECHADO : ABERTO;
        btn.setAttribute('aria-label', mostrando ? 'Mostrar senha' : 'Ocultar senha');
        btn.setAttribute('title', mostrando ? 'Mostrar senha' : 'Ocultar senha');
      });
    });
  }

  function iniciarSair() {
    $$('[data-acao="sair"]').forEach(function (b) {
      b.addEventListener('click', function (e) {
        e.preventDefault();
        limparSessao();
        guardarAviso('Você saiu da sua conta.');
        window.location.href = PAGINAS.login;
      });
    });
    var s = lerSessao();
    var rotulo = $('#menu-usuario');
    if (rotulo && s) rotulo.textContent = '👤 ' + s.nome;
  }

  function confirmar(opcoes) {
    return new Promise(function (resolver) {
      var anterior = document.activeElement;
      var fundo = document.createElement('div');
      fundo.className = 'modal-fundo';
      fundo.innerHTML =
        '<div class="modal" role="alertdialog" aria-modal="true" aria-labelledby="modal-titulo" aria-describedby="modal-texto">' +
        '<h2 id="modal-titulo">' + esc(opcoes.titulo) + '</h2><p id="modal-texto">' + esc(opcoes.texto) + '</p>' +
        '<div class="modal-acoes"><button type="button" class="btn btn-secundario">Cancelar</button>' +
        '<button type="button" class="btn ' + (opcoes.perigo ? 'btn-perigo' : 'btn-primario') + '">' + esc(opcoes.confirmar || 'Confirmar') + '</button></div></div>';
      document.body.appendChild(fundo);
      var botoes = fundo.querySelectorAll('button');
      function fechar(valor) {
        document.removeEventListener('keydown', tecla, true);
        fundo.remove();
        if (anterior && anterior.focus) anterior.focus();
        resolver(valor);
      }
      function tecla(e) {
        if (e.key === 'Escape') { e.preventDefault(); fechar(false); }
        else if (e.key === 'Tab') {
          var ativo = document.activeElement;
          if (e.shiftKey && (ativo === botoes[0] || !fundo.contains(ativo))) { e.preventDefault(); botoes[1].focus(); }
          else if (!e.shiftKey && (ativo === botoes[1] || !fundo.contains(ativo))) { e.preventDefault(); botoes[0].focus(); }
        }
      }
      document.addEventListener('keydown', tecla, true);
      fundo.addEventListener('click', function (e) { if (e.target === fundo) fechar(false); });
      botoes[0].addEventListener('click', function () { fechar(false); });
      botoes[1].addEventListener('click', function () { fechar(true); });
      botoes[0].focus();
    });
  }

  /* ---------- Cartão de tarefa (resumido, usado no dashboard) ---------- */
  function htmlMini(t) {
    var atraso = estaAtrasada(t) ? ' · <span class="tag-atraso">Atrasada</span>' : '';
    return '<a class="mini' + (t.concluida ? ' mini-concluida' : '') + '" href="' + PAGINAS.editar + '?id=' + t.id + '">' +
      '<span class="mini-info"><span class="mini-titulo">' + esc(t.titulo) + '</span>' +
      '<span class="mini-meta">' + esc(t.tipo || 'Geral') + ' · ' + (t.prazo ? 'até ' + isoParaBR(t.prazo) : 'sem prazo') + atraso + '</span></span>' +
      '<span class="selo selo-' + classePrioridade(t.prioridade) + '">' + esc(t.prioridade || 'Média') + '</span></a>';
  }

  /* ====================== PÁGINAS ====================== */

  function paginaLogin() {
    if (lerSessao()) { window.location.replace(PAGINAS.dashboard); return; }
    var form = $('#form-login'), campoLogin = $('#login-usuario'), campoSenha = $('#senha-login');
    var lembrar = $('#lembrar'), status = $('#status-msg'), botao = $('#btn-entrar');
    iniciarOlhos();
    limparErrosAoDigitar([campoLogin, campoSenha]);

    var aviso = lerAviso();
    if (aviso) mostrar(status, 'info', aviso);

    $('#btn-esqueci').addEventListener('click', function () {
      mostrar(status, 'info', 'Para redefinir a sua senha, procure o administrador do sistema.');
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var login = campoLogin.value.trim(), senha = campoSenha.value.trim();
      var ok = true;
      ok = erroCampo(campoLogin, login ? '' : 'Informe seu e-mail ou nome de usuário.') && ok;
      ok = erroCampo(campoSenha, senha ? '' : 'Informe sua senha.') && ok;
      if (!ok) { mostrar(status, 'erro', '⚠️ Preencha todos os campos para entrar.'); focarPrimeiroErro([campoLogin, campoSenha]); return; }

      botao.disabled = true;
      mostrar(status, 'info', '⏳ Verificando seus dados...');
      api('/usuarios/login', { metodo: 'POST', form: { username: login, password: senha }, auth: false }).then(function (r) {
        if (!r.ok) {
          botao.disabled = false;
          mostrar(status, 'erro', '⚠️ ' + (r.status === 401 ? 'Usuário/e-mail ou senha incorretos. Confira os dados e tente novamente.' : r.erro));
          if (r.status === 401) { campoSenha.value = ''; campoSenha.focus(); }
          return;
        }
        var d = r.data;
        salvarSessao({ token: d.access_token, id: d.id, nome: d.nome, email: d.email, papel: d.papel, estilo: d.estilo_instrucao }, lembrar.checked);
        mostrar(status, 'sucesso', '✅ Login efetuado com sucesso! Entrando...');
        setTimeout(function () { irPara('dashboard'); }, 500);
      });
    });
  }

  function paginaCadastro() {
    if (lerSessao()) { window.location.replace(PAGINAS.dashboard); return; }
    var form = $('#form-cadastro'), status = $('#status-msg'), botao = $('#btn-criar-conta');
    var cNome = $('#nome-usuario'), cEmail = $('#email-usuario'), cSenha = $('#senha-usuario');
    var cConf = $('#confirma-senha-usuario'), cEstilo = $('#estilo-usuario');
    var campos = [cNome, cEmail, cSenha, cConf];
    iniciarOlhos();
    limparErrosAoDigitar(campos);

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var nome = cNome.value.trim(), email = cEmail.value.trim(), senha = cSenha.value.trim(), conf = cConf.value.trim();
      var ok = true;
      ok = erroCampo(cNome, !nome ? 'Preencha o nome completo.' : nome.length < 2 ? 'O nome deve ter pelo menos 2 caracteres.' : nome.indexOf('@') >= 0 ? 'O nome não pode conter @.' : '') && ok;
      ok = erroCampo(cEmail, !email ? 'Preencha o e-mail.' : !REGEX_EMAIL.test(email) ? 'Use o formato seu@email.com.' : '') && ok;
      ok = erroCampo(cSenha, !senha ? 'Crie uma senha.' : senha.length < 6 ? 'A senha deve ter pelo menos 6 caracteres.' : '') && ok;
      ok = erroCampo(cConf, !conf ? 'Repita a senha.' : (senha && conf !== senha) ? 'As senhas não são iguais.' : '') && ok;
      if (!ok) { mostrar(status, 'erro', '⚠️ Corrija os campos indicados para continuar.'); focarPrimeiroErro(campos); return; }

      botao.disabled = true;
      mostrar(status, 'info', '⏳ Criando a sua conta...');
      api('/usuarios', { metodo: 'POST', auth: false, corpo: { nome: nome, email: email, senha: senha, estilo_instrucao: cEstilo.value } }).then(function (r) {
        if (!r.ok) { botao.disabled = false; mostrar(status, 'erro', '⚠️ ' + r.erro); return; }
        // Conta criada: já entra automaticamente.
        return api('/usuarios/login', { metodo: 'POST', form: { username: email, password: senha }, auth: false }).then(function (l) {
          if (l.ok) {
            var d = l.data;
            salvarSessao({ token: d.access_token, id: d.id, nome: d.nome, email: d.email, papel: d.papel, estilo: d.estilo_instrucao }, false);
            mostrar(status, 'sucesso', '✅ Conta criada com sucesso! Entrando...');
            setTimeout(function () { irPara('dashboard'); }, 700);
          } else {
            guardarAviso('Conta criada com sucesso! Faça login para continuar.');
            irPara('login');
          }
        });
      });
    });
  }

  function paginaDashboard() {
    var s = exigirLogin(); if (!s) return;
    iniciarSair();
    $('#nome-usuario-logado').textContent = primeiroNome(s.nome);
    var status = $('#status-msg'), lista = $('#lista-proximas'), busca = $('#input-pesquisa');
    var titulo = $('#titulo-lista'), verTodas = $('#link-ver-todas');
    var tarefas = [];

    function desenhar() {
      var termo = busca.value.trim().toLowerCase();
      var ordenadas = ordenarTarefas(tarefas);
      var itens;
      if (termo) {
        itens = ordenadas.filter(function (t) {
          return (t.titulo + ' ' + (t.tipo || '') + ' ' + (t.descricao || '')).toLowerCase().indexOf(termo) >= 0;
        });
        titulo.textContent = 'Resultado da pesquisa';
      } else {
        itens = ordenadas.filter(function (t) { return !t.concluida; }).slice(0, 5);
        titulo.textContent = 'Próximas tarefas';
      }
      if (!itens.length) {
        lista.innerHTML = termo
          ? '<div class="vazio">🔎 Nenhuma tarefa encontrada para "' + esc(busca.value.trim()) + '".</div>'
          : '<div class="vazio">🎉 Você não tem tarefas pendentes.<br><a class="link-botao" href="' + PAGINAS.criar + '">Criar uma nova tarefa</a></div>';
        return;
      }
      lista.innerHTML = itens.map(htmlMini).join('');
    }

    function resumir() {
      var pend = tarefas.filter(function (t) { return !t.concluida; }).length;
      $('#num-pendentes').textContent = pend;
      $('#num-concluidas').textContent = tarefas.length - pend;
      $('#num-atrasadas').textContent = tarefas.filter(estaAtrasada).length;
    }

    mostrar(status, 'info', '⏳ Carregando suas tarefas...');
    api('/tarefas').then(function (r) {
      if (!r.ok) { mostrar(status, 'erro', '⚠️ ' + r.erro); lista.innerHTML = ''; return; }
      tarefas = r.data.dados || [];
      mostrar(status, 'info', '');
      resumir(); desenhar();
    });
    busca.addEventListener('input', desenhar);
    verTodas.setAttribute('href', PAGINAS.tarefas);
  }

  function paginaTarefas() {
    var s = exigirLogin(); if (!s) return;
    iniciarSair();
    var status = $('#status-msg'), lista = $('#lista-tarefas'), busca = $('#input-pesquisa');
    var botaoAtualizar = $('#btn-atualizar'), botaoLimpar = $('#btn-limpar-concluidas');
    var filtro = 'todas', tarefas = [];

    function desenhar() {
      var termo = busca.value.trim().toLowerCase();
      var itens = ordenarTarefas(tarefas).filter(function (t) {
        if (filtro === 'pendentes' && t.concluida) return false;
        if (filtro === 'concluidas' && !t.concluida) return false;
        return !termo || (t.titulo + ' ' + (t.tipo || '') + ' ' + (t.descricao || '')).toLowerCase().indexOf(termo) >= 0;
      });
      if (!itens.length) {
        lista.innerHTML = '<div class="vazio">📭 ' + (tarefas.length
          ? 'Nenhuma tarefa corresponde ao filtro ou à pesquisa.'
          : 'Você ainda não tem tarefas.<br>Clique em <strong>Criar Tarefa</strong> para começar.') + '</div>';
        return;
      }
      lista.innerHTML = itens.map(function (t) {
        var atraso = estaAtrasada(t) ? ' · <span class="tag-atraso">Atrasada</span>' : '';
        return '<article class="tarefa' + (t.concluida ? ' tarefa-concluida' : '') + '">' +
          '<div class="tarefa-topo"><label class="tarefa-check"><input type="checkbox" class="caixa" data-acao="alternar" data-id="' + t.id + '"' + (t.concluida ? ' checked' : '') + '>' +
          '<span class="tarefa-titulo">' + esc(t.titulo) + '</span></label>' +
          '<span class="selo selo-' + classePrioridade(t.prioridade) + '">' + esc(t.prioridade || 'Média') + '</span></div>' +
          '<p class="tarefa-meta">📅 ' + (t.prazo ? isoParaBR(t.prazo) : 'Sem prazo') + ' · 🏷️ ' + esc(t.tipo || 'Geral') + atraso + '</p>' +
          (t.descricao ? '<p class="tarefa-desc">' + esc(t.descricao) + '</p>' : '') +
          '<div class="tarefa-acoes"><a class="btn btn-secundario btn-pequeno" href="' + PAGINAS.editar + '?id=' + t.id + '">✏️ Editar</a>' +
          '<button type="button" class="btn btn-perigo btn-pequeno" data-acao="excluir" data-id="' + t.id + '" data-titulo="' + esc(t.titulo) + '">🗑️ Excluir</button></div></article>';
      }).join('');
    }

    function contagem() {
      var pend = tarefas.filter(function (t) { return !t.concluida; }).length;
      mostrar(status, 'info', tarefas.length
        ? tarefas.length + ' tarefa(s): ' + pend + ' pendente(s) e ' + (tarefas.length - pend) + ' concluída(s).'
        : '');
    }

    function carregar() {
      mostrar(status, 'info', '⏳ Carregando suas tarefas...');
      return api('/tarefas').then(function (r) {
        if (!r.ok) { mostrar(status, 'erro', '⚠️ ' + r.erro); return; }
        tarefas = r.data.dados || [];
        contagem(); desenhar();
      });
    }

    lista.addEventListener('change', function (e) {
      var alvo = e.target;
      if (alvo.getAttribute('data-acao') !== 'alternar') return;
      var id = Number(alvo.getAttribute('data-id')), marcada = alvo.checked;
      alvo.disabled = true;
      api('/tarefas/' + id + '/concluida', { metodo: 'PATCH', corpo: { concluida: marcada } }).then(function (r) {
        if (!r.ok) { alvo.checked = !marcada; alvo.disabled = false; mostrar(status, 'erro', '⚠️ ' + r.erro); return; }
        tarefas.forEach(function (t) { if (t.id === id) t.concluida = marcada; });
        desenhar(); contagem();
        mostrar(status, 'sucesso', marcada ? '✅ Tarefa marcada como concluída.' : '↩️ Tarefa marcada como pendente.');
      });
    });

    lista.addEventListener('click', function (e) {
      var botao = e.target.closest('[data-acao="excluir"]');
      if (!botao) return;
      var id = Number(botao.getAttribute('data-id'));
      confirmar({ titulo: 'Excluir tarefa?', texto: 'A tarefa "' + botao.getAttribute('data-titulo') + '" será removida definitivamente.', confirmar: 'Excluir', perigo: true }).then(function (sim) {
        if (!sim) return;
        api('/tarefas/' + id, { metodo: 'DELETE' }).then(function (r) {
          if (!r.ok) { mostrar(status, 'erro', '⚠️ ' + r.erro); return; }
          tarefas = tarefas.filter(function (t) { return t.id !== id; });
          desenhar();
          mostrar(status, 'sucesso', '🗑️ Tarefa excluída com sucesso.');
        });
      });
    });

    $$('.filtro').forEach(function (b) {
      b.addEventListener('click', function () {
        filtro = b.getAttribute('data-filtro');
        $$('.filtro').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        desenhar();
      });
    });
    busca.addEventListener('input', desenhar);

    botaoAtualizar.addEventListener('click', function () {
      botaoAtualizar.disabled = true;
      carregar().then(function () { botaoAtualizar.disabled = false; });
    });

    botaoLimpar.addEventListener('click', function () {
      if (!tarefas.some(function (t) { return t.concluida; })) { mostrar(status, 'info', 'ℹ️ Não há tarefas concluídas para remover.'); return; }
      confirmar({ titulo: 'Limpar tarefas concluídas?', texto: 'Todas as tarefas concluídas serão removidas definitivamente.', confirmar: 'Limpar', perigo: true }).then(function (sim) {
        if (!sim) return;
        api('/tarefas/concluidas', { metodo: 'DELETE' }).then(function (r) {
          if (!r.ok) { mostrar(status, 'erro', '⚠️ ' + r.erro); return; }
          tarefas = tarefas.filter(function (t) { return !t.concluida; });
          desenhar();
          mostrar(status, 'sucesso', '✨ ' + r.data.mensagem);
        });
      });
    });

    carregar();
  }

  function paginaFormTarefa() {
    var s = exigirLogin(); if (!s) return;
    iniciarSair();
    var editando = document.body.getAttribute('data-modo') === 'editar';
    var form = $('#form-tarefa'), status = $('#status-msg'), botao = $('#btn-salvar-tarefa');
    var cTitulo = $('#titulo-tarefa'), cTipo = $('#tipo-tarefa'), cPrio = $('#prioridade-tarefa');
    var cPrazo = $('#prazo-tarefa'), cDesc = $('#descricao-tarefa');
    var campos = [cTitulo, cTipo, cPrazo];
    var id = new URLSearchParams(window.location.search).get('id');

    mascaraData(cPrazo);
    limparErrosAoDigitar(campos);

    if (editando) {
      if (!id) { mostrar(status, 'erro', '⚠️ Nenhuma tarefa foi selecionada para edição.'); form.querySelectorAll('input,select,textarea,button').forEach(function (c) { c.disabled = true; }); return; }
      mostrar(status, 'info', '⏳ Carregando a tarefa...');
      api('/tarefas/' + encodeURIComponent(id)).then(function (r) {
        if (!r.ok) {
          mostrar(status, 'erro', '⚠️ ' + r.erro);
          form.querySelectorAll('input,select,textarea,button').forEach(function (c) { c.disabled = true; });
          return;
        }
        var t = r.data.dados;
        cTitulo.value = t.titulo || ''; cTipo.value = t.tipo || ''; cPrio.value = t.prioridade || 'Média';
        cPrazo.value = isoParaBR(t.prazo); cDesc.value = t.descricao || '';
        mostrar(status, 'info', '');
        cTitulo.focus();
      });
    } else {
      cPrazo.value = hojeBR();
      cTitulo.focus();
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var titulo = cTitulo.value.trim(), tipo = cTipo.value.trim() || 'Geral', prazoBR = cPrazo.value.trim();
      var prazoISO = brParaISO(prazoBR);
      var ok = true;
      ok = erroCampo(cTitulo, !titulo ? 'Informe o título da tarefa.' : titulo.length < 3 ? 'O título deve ter pelo menos 3 caracteres.' : '') && ok;
      ok = erroCampo(cPrazo, !prazoBR ? 'Informe o prazo.' : !prazoISO ? 'Data inválida. Use o formato DD/MM/AAAA.' : '') && ok;
      if (!ok) { mostrar(status, 'erro', '⚠️ Corrija os campos indicados para continuar.'); focarPrimeiroErro(campos); return; }

      botao.disabled = true;
      mostrar(status, 'info', editando ? '⏳ Salvando alterações...' : '⏳ Salvando tarefa...');
      var corpo = { titulo: titulo, tipo: tipo, prioridade: cPrio.value, prazo: prazoISO, descricao: cDesc.value.trim() || null };
      api(editando ? '/tarefas/' + encodeURIComponent(id) : '/tarefas', { metodo: editando ? 'PUT' : 'POST', corpo: corpo }).then(function (r) {
        if (!r.ok) { botao.disabled = false; mostrar(status, 'erro', '⚠️ ' + r.erro); return; }
        mostrar(status, 'sucesso', editando ? '✅ Tarefa atualizada com sucesso!' : '✅ Tarefa criada com sucesso!');
        setTimeout(function () { irPara('tarefas'); }, 700);
      });
    });
  }

  function paginaUsuarios() {
    var s = exigirLogin(); if (!s) return;
    iniciarSair();
    var status = $('#status-msg'), lista = $('#lista-usuarios');
    var souAdmin = s.papel === 'admin';

    function desenhar(usuarios) {
      if (!usuarios.length) { lista.innerHTML = '<div class="vazio">Nenhum usuário cadastrado.</div>'; return; }
      lista.innerHTML = usuarios.map(function (u) {
        var podeExcluir = souAdmin && u.id !== s.id;
        return '<div class="cartao-usuario"><div class="usuario-nome">👤 ' + esc(u.nome) + (u.id === s.id ? ' (você)' : '') + '</div>' +
          '<div class="usuario-meta">✉️ ' + esc(u.email || 'E-mail não informado') + '</div>' +
          '<div class="usuario-meta">🛡️ ' + (u.papel === 'admin' ? 'Administrador' : 'Usuário') + ' · Estilo do Murphy: ' + esc(u.estilo_instrucao || 'direto') + '</div>' +
          (podeExcluir ? '<button type="button" class="btn btn-perigo btn-pequeno" data-acao="excluir" data-id="' + u.id + '" data-nome="' + esc(u.nome) + '">🗑️ Excluir usuário</button>' : '') + '</div>';
      }).join('');
    }

    function carregar(mensagemFinal) {
      mostrar(status, 'info', '⏳ Carregando usuários...');
      api('/usuarios').then(function (r) {
        if (!r.ok) { mostrar(status, 'erro', '⚠️ ' + r.erro); return; }
        var usuarios = r.data.dados || [];
        if (mensagemFinal) mostrar(status, 'sucesso', mensagemFinal);
        else mostrar(status, 'info', usuarios.length + ' usuário(s) cadastrado(s).');
        desenhar(usuarios);
      });
    }

    lista.addEventListener('click', function (e) {
      var b = e.target.closest('[data-acao="excluir"]');
      if (!b) return;
      confirmar({ titulo: 'Excluir usuário?', texto: 'O usuário "' + b.getAttribute('data-nome') + '" e todas as tarefas dele serão removidos definitivamente.', confirmar: 'Excluir', perigo: true }).then(function (sim) {
        if (!sim) return;
        api('/usuarios/' + b.getAttribute('data-id'), { metodo: 'DELETE' }).then(function (r) {
          if (!r.ok) { mostrar(status, 'erro', '⚠️ ' + r.erro); return; }
          carregar('🗑️ ' + (r.data.mensagem || 'Usuário excluído com sucesso.'));
        });
      });
    });
    carregar();
  }

  /* ---------- Chat com o Murphy ---------- */
  function renderMarkdown(origem) {
    var texto = esc(origem), blocos = [];
    texto = texto.replace(/```(?:\w+)?\n?([\s\S]*?)```/g, function (m, c) { blocos.push(c.replace(/\n$/, '')); return '@@BLOCO' + (blocos.length - 1) + '@@'; });
    function inline(t) {
      return t.replace(/`([^`]+)`/g, '<code>$1</code>').replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/(^|[\s(])\*([^*\s][^*]*)\*/g, '$1<em>$2</em>');
    }
    var html = '', lista = null;
    function fechar() { if (lista) { html += '</' + lista + '>'; lista = null; } }
    texto.split('\n').forEach(function (linha) {
      var m;
      if ((m = linha.match(/^\s*[-*•]\s+(.*)/))) { if (lista !== 'ul') { fechar(); html += '<ul>'; lista = 'ul'; } html += '<li>' + inline(m[1]) + '</li>'; }
      else if ((m = linha.match(/^\s*\d+[.)]\s+(.*)/))) { if (lista !== 'ol') { fechar(); html += '<ol>'; lista = 'ol'; } html += '<li>' + inline(m[1]) + '</li>'; }
      else if ((m = linha.match(/^#{1,6}\s+(.*)/))) { fechar(); html += '<p><strong>' + inline(m[1]) + '</strong></p>'; }
      else if (linha.trim() === '') { fechar(); }
      else { fechar(); html += '<p>' + inline(linha) + '</p>'; }
    });
    fechar();
    html = html.replace(/<p>@@BLOCO(\d+)@@<\/p>/g, '@@BLOCO$1@@').replace(/@@BLOCO(\d+)@@/g, function (m, i) { return '<pre><code>' + blocos[i] + '</code></pre>'; });
    return html;
  }

  function paginaChat() {
    var s = exigirLogin(); if (!s) return;
    iniciarSair();
    var SUGESTOES = ['📋 O que tenho pendente?', '🎯 Me ajude a priorizar meu dia', '🧩 Quebre uma tarefa em passos', '💡 Dicas para manter o foco'];
    var caixa = $('#chat-mensagens'), sugestoes = $('#sugestoes'), form = $('#form-chat');
    var entrada = $('#user-input'), enviarBtn = $('#send-btn'), limparBtn = $('#clear-btn'), estilo = $('#estilo-murphy');
    var primeiro = primeiroNome(s.nome);
    var CHAVE_HIST = 'murphy_historico_' + s.id;
    var historico = [], aguardando = false;
    try { historico = JSON.parse(window.localStorage.getItem(CHAVE_HIST)) || []; } catch (e) { historico = []; }
    function salvarHist() { try { window.localStorage.setItem(CHAVE_HIST, JSON.stringify(historico.slice(-40))); } catch (e) {} }
    function rolar() { caixa.scrollTop = caixa.scrollHeight; }

    function addMsg(papel, texto) {
      var div = document.createElement('div');
      div.className = 'msg ' + (papel === 'user' ? 'usuario' : 'ia');
      div.innerHTML = '<span class="msg-autor">' + (papel === 'user' ? 'VOCÊ' : 'MURPHY 🤖') + '</span><div class="msg-corpo">' +
        (papel === 'user' ? '<p>' + esc(texto) + '</p>' : renderMarkdown(texto)) + '</div>';
      caixa.appendChild(div); rolar(); return div;
    }
    function digitando() {
      var div = document.createElement('div');
      div.className = 'msg ia';
      div.innerHTML = '<span class="msg-autor">MURPHY 🤖</span><div class="digitando" aria-label="Murphy está digitando"><span></span><span></span><span></span></div>';
      caixa.appendChild(div); rolar(); return div;
    }
    function mostrarErro(texto, divUsuario, detalhe) {
      var div = document.createElement('div');
      div.className = 'msg ia erro';
      div.innerHTML = '<span class="msg-autor">MURPHY 🤖</span><div class="msg-corpo"><p>' + esc(detalhe) + '</p></div>';
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'btn btn-primario btn-pequeno chat-tentar'; b.textContent = '🔄 Tentar novamente';
      b.addEventListener('click', function () { div.remove(); if (divUsuario) divUsuario.remove(); enviar(texto); });
      div.appendChild(b); caixa.appendChild(div); rolar();
    }
    function ocupado(sim) {
      aguardando = sim; enviarBtn.disabled = sim; entrada.disabled = sim;
      if (!sim) entrada.focus();
    }
    function mostrarSugestoes() {
      sugestoes.innerHTML = '';
      SUGESTOES.forEach(function (t) {
        var b = document.createElement('button');
        b.type = 'button'; b.className = 'sugestao'; b.textContent = t;
        b.addEventListener('click', function () { enviar(t.replace(/^\S+\s/, '')); });
        sugestoes.appendChild(b);
      });
    }
    function iniciar() {
      caixa.innerHTML = '';
      addMsg('model', 'Oi' + (primeiro ? ', ' + primeiro : '') + '! Eu sou o Murphy, seu assistente aqui no FOCUS. Posso bater um papo, tirar dúvidas, te ajudar a organizar o dia ou quebrar uma tarefa grande em passos pequenos. Sobre o que vamos falar?');
      historico.forEach(function (m) { addMsg(m.papel, m.texto); });
      if (!historico.length) mostrarSugestoes(); else sugestoes.innerHTML = '';
    }

    function enviar(texto) {
      texto = (texto || '').trim();
      if (!texto || aguardando) return;
      ocupado(true); sugestoes.innerHTML = ''; entrada.value = '';
      var divUsuario = addMsg('user', texto), espera = digitando();
      var ctrl = new AbortController(), limite = setTimeout(function () { ctrl.abort(); }, 120000);

      var sessao = lerSessao();
      fetch(API + '/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + (sessao ? sessao.token : '') },
        body: JSON.stringify({ comando: texto, historico: historico.slice(-12) }),
        signal: ctrl.signal
      }).then(function (resp) {
        clearTimeout(limite);
        return resp.json().catch(function () { return {}; }).then(function (data) {
          espera.remove();
          if (resp.status === 401) { limparSessao(); guardarAviso(extrairErro(data, 401)); window.location.replace(PAGINAS.login); return; }
          if (!resp.ok) { mostrarErro(texto, divUsuario, extrairErro(data, resp.status)); return; }
          addMsg('model', data.resposta);
          historico.push({ papel: 'user', texto: texto }, { papel: 'model', texto: data.resposta });
          salvarHist();
        });
      }).catch(function (erro) {
        clearTimeout(limite); espera.remove();
        mostrarErro(texto, divUsuario, erro && erro.name === 'AbortError'
          ? 'A resposta demorou demais. Vamos tentar de novo?'
          : 'Não consegui me conectar ao servidor. Verifique se o sistema está ligado.');
      }).then(function () { ocupado(false); });
    }

    limparBtn.addEventListener('click', function () {
      if (aguardando) return;
      historico = [];
      try { window.localStorage.removeItem(CHAVE_HIST); } catch (e) {}
      iniciar();
    });
    form.addEventListener('submit', function (e) { e.preventDefault(); enviar(entrada.value); });

    estilo.value = s.estilo === 'detalhado' ? 'detalhado' : 'direto';
    estilo.addEventListener('change', function () {
      var novo = estilo.value;
      api('/usuarios/me', { metodo: 'PATCH', corpo: { estilo_instrucao: novo } }).then(function (r) {
        if (r.ok) atualizarSessao({ estilo: novo });
      });
    });

    iniciar();
    entrada.focus();
  }

  var ROTAS = { login: paginaLogin, cadastro: paginaCadastro, dashboard: paginaDashboard, tarefas: paginaTarefas, formTarefa: paginaFormTarefa, usuarios: paginaUsuarios, chat: paginaChat };
  document.addEventListener('DOMContentLoaded', function () {
    var pagina = document.body.getAttribute('data-pagina');
    if (ROTAS[pagina]) ROTAS[pagina]();
  });

  // Exposto para testes/depuração
  window.Focus = { brParaISO: brParaISO, isoParaBR: isoParaBR, extrairErro: extrairErro, renderMarkdown: renderMarkdown, esc: esc };
})();