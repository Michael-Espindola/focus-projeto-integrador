# Contrato da API - FOCUS

Base: `http://127.0.0.1:8000` · Documentação interativa: `/docs`
Rotas protegidas exigem o cabeçalho `Authorization: Bearer <token>` (token obtido no login).
Erros sempre vêm como `{"detail": "mensagem em português"}`.

| # | Nome | Método | Caminho | Token? | Quem pode |
|---|------|--------|---------|--------|-----------|
| 1 | Cadastrar usuário | POST | `/usuarios` | Não | Público (papel sempre `usuario`) |
| 2 | Login | POST | `/usuarios/login` | Não | Público |
| 3 | Listar usuários | GET | `/usuarios` | Sim | Qualquer logado |
| 4 | Ver perfil (/me) | GET | `/usuarios/perfil/me` | Sim | Qualquer logado |
| 5 | Alterar meu estilo do Murphy | PATCH | `/usuarios/me` | Sim | Qualquer logado |
| 6 | Buscar usuário por ID | GET | `/usuarios/{id}` | Sim | Qualquer logado |
| 7 | Excluir usuário | DELETE | `/usuarios/{id}` | Sim | Somente `admin` |
| 8 | Listar minhas tarefas | GET | `/tarefas` | Sim | Dono |
| 9 | Criar tarefa | POST | `/tarefas` | Sim | Dono |
| 10 | Buscar tarefa | GET | `/tarefas/{id}` | Sim | Dono |
| 11 | Editar tarefa | PUT | `/tarefas/{id}` | Sim | Dono |
| 12 | Concluir/reabrir tarefa | PATCH | `/tarefas/{id}/concluida` | Sim | Dono |
| 13 | Excluir tarefa | DELETE | `/tarefas/{id}` | Sim | Dono |
| 14 | Limpar concluídas | DELETE | `/tarefas/concluidas` | Sim | Dono |
| 15 | Conversar com o Murphy | POST | `/api/chat` | Sim | Qualquer logado |

## Corpos de entrada
- **POST /usuarios**: `{"nome":"João Silva","email":"joao@email.com","senha":"123456","estilo_instrucao":"direto"}` (senha mín. 6; estilo `direto` ou `detalhado`)
- **POST /usuarios/login**: formulário `username` (nome ou e-mail) e `password` (`x-www-form-urlencoded`)
- **POST/PUT /tarefas**: `{"titulo":"Estudar","tipo":"Estudos","prioridade":"Alta","prazo":"2026-12-31","descricao":"opcional"}` (prioridade: Alta, Média ou Baixa; prazo `AAAA-MM-DD`)
- **PATCH /tarefas/{id}/concluida**: `{"concluida": true}`
- **POST /api/chat**: `{"comando":"O que tenho pendente?","historico":[{"papel":"user","texto":"..."}]}`

## Respostas de sucesso
- Login `200`: `{"access_token":"...","token_type":"bearer","id":1,"nome":"Michael","email":"...","papel":"admin","estilo_instrucao":"direto"}`
- Cadastro/criação `201`: `{"sucesso":true,"mensagem":"...","dados":{...}}`
- Listagens `200`: `{"sucesso":true,"dados":[...]}`

## Erros possíveis
`401` sessão ausente/expirada ou login incorreto · `403` sem permissão · `404` não encontrado (inclui tarefa de outra pessoa) · `422` dados inválidos/regra de negócio · `503` IA indisponível · `500` erro interno.

## Segurança
Senhas guardadas com hash (PBKDF2); contas antigas em texto puro são convertidas no primeiro login. Cada usuário só vê e altera as próprias tarefas. O token expira (`JWT_EXPIRE_MINUTES`).
