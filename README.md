# 🚀 Dashboard Financeiro de Vendas

Sistema de monitoramento em tempo real de vendas de supermercados com visualização de métricas financeiras.

## 📋 Requisitos

- Python 3.8+
- Acesso ao banco de dados IBM DB2
- Node.js ou qualquer navegador moderno

## 🛠️ Setup Local

### 1. Clonar/Preparar repositório
```bash
# Se estiver usando Git
git clone seu_repositorio
cd dashboard-vendas
```

### 2. Criar arquivo .env
Crie um arquivo `.env` na raiz do projeto baseado em `.env.example`:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

Edite o `.env` com suas credenciais:
```env
DB_HOST=SUPERMERCADOSVITORIADB.DATACISS.COM.BR
DB_PORT=50022
DB_NAME=VITORIA
DB_USER=vitoria
DB_PASSWORD=sua_senha_aqui
FLASK_ENV=development
```

### 3. Instalar dependências
```powershell
# Windows
python -m pip install -r requirements.txt

# Ou se python não estiver no PATH
py -m pip install -r requirements.txt

# Linux/Mac
pip install -r requirements.txt
```

**Dependências instaladas**:
- `Flask`: servidor web
- `ibm_db`: driver DB2
- `gunicorn`: production server
- `python-dotenv`: carrega variáveis de ambiente

### 4. Verificar conexão ao DB2

Antes de iniciar, confirme:
- ✅ Host do DB2 acessível
- ✅ Porta 50022 liberada no firewall
- ✅ Banco `VITORIA` disponível
- ✅ Usuário e senha válidos
- ✅ Permissão de leitura nas tabelas

### 5. Rodar aplicação localmente
```powershell
python app.py
```

Acesse em `http://localhost:5000`

## 🌐 Deploy no Render

### Pré-requisitos
- Conta em [Render.com](https://render.com)
- Repositório GitHub com o código
- Arquivo `.env` configurado (mas nunca commit com credenciais)

### Passos para Deploy

#### 1. Preparar Repositório GitHub
```bash
# Verificar se .env está no .gitignore (deve estar)
git status

# Adicionar arquivos necessários
git add requirements.txt Procfile .env.example .gitignore app.py index.html app.js style.css

# Commit
git commit -m "Preparar para deploy no Render"

# Push
git push origin main
```

#### 2. Conectar GitHub ao Render
1. Faça login em [render.com](https://render.com)
2. Clique em **"New +"** → **"Web Service"**
3. Selecione **"Build and deploy from a Git repository"**
4. Conecte sua conta GitHub
5. Selecione o repositório

#### 3. Configurar o Serviço
Preencha conforme abaixo:

| Campo | Valor |
|-------|-------|
| **Name** | `dashboard-vendas` |
| **Repository** | seu_repositorio |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Plan** | `Free` (inicia com free) |

#### 4. Adicionar Variáveis de Ambiente
1. No dashboard do Render, vá até seu serviço
2. Clique em **"Environment"**
3. Adicione cada variável:

```
DB_HOST=SUPERMERCADOSVITORIADB.DATACISS.COM.BR
DB_PORT=50022
DB_NAME=VITORIA
DB_USER=vitoria
DB_PASSWORD=sua_senha_super_segura_aqui
FLASK_ENV=production
```

**Nunca coloque essas informações no GitHub!**

#### 5. Deploy
1. Clique em **"Create Web Service"**
2. Render fará o build automaticamente
3. Aguarde até ficar **verde ✓ Live**
4. Seu dashboard estará em: `https://dashboard-vendas.onrender.com`

## 📂 Estrutura de Arquivos

```
dashboard-vendas/
├── app.py                      # Backend Flask (API)
├── index.html                  # Frontend HTML
├── app.js                      # Lógica JavaScript
├── style.css                   # Estilos CSS
├── requirements.txt            # Dependências Python
├── Procfile                    # Config para Render (sem extensão)
├── .env.example                # Modelo de variáveis (commit este)
├── .gitignore                  # Git ignore rules
├── cache_vendas.json          # Cache local (gerado automaticamente)
├── README.md                   # Este arquivo
└── DOCUMENTACAO_SISTEMA.md     # Documentação técnica detalhada
```

## 🔐 Segurança - Importante!

### Nunca commit `.env` com credenciais!

1. O `.gitignore` já protege o arquivo `.env`
2. Sempre use `.env.example` como modelo
3. Credenciais devem estar apenas em:
   - `.env` local (não commitado)
   - Variáveis de ambiente no Render

Verifique se não subiu credenciais:
```bash
git log --all --full-history -- app.py | grep -i password
```

## 🔄 Atualizações em Tempo Real

- **Frequência**: A cada ~5 segundos
- **Sistema**: Requisições HTTP a cada 2s com timeout de 5s
- **Cache**: Fallback automático se DB2 indisponível
- **Status**: Visual indica se dados são "AO VIVO", "CACHE" ou "OFFLINE"

## 📊 Métricas Monitoradas

✅ Total Vendido Hoje
✅ Horário de Pico
✅ Quantidade de Transações
✅ Ticket Médio
✅ Margem de Lucro
✅ Gráfico de Vendas por Hora
✅ Faturamento por Loja (Hoje)
✅ Faturamento Acumulado (Mês)

## 🚨 Troubleshooting

### Erro: "No module named ibm_db"
```powershell
python -m pip install -r requirements.txt --upgrade
```

### Erro: "Connection refused" ao DB2
- ✅ Verifique credenciais no `.env`
- ✅ Confirme if DB2 está online
- ✅ Teste conectividade: `Test-NetConnection -ComputerName seu_host -Port 50022`

### Dashboard mostra "CACHE" ou "OFFLINE"
- Significa que o backend não conseguiu conectar ao DB2
- Verifique logs: `tail -f /path/to/logs` (Render)
- Dados podem estar desatualizados, mas o sistema ainda funciona

### Página branca/vazia
- Abra DevTools (F12)
- Vá para aba "Console"
- Verifique se há erros
- Confirme se servidor está rodando

### Não acessa `http://localhost:5000`
- Confirme if `python app.py` está rodando
- Tente `http://127.0.0.1:5000`
- Verifique if porta 5000 já está em uso: `netstat -an | findstr :5000`

## 📞 Suporte Técnico

Para informações detalhadas sobre:
- Arquitetura do sistema
- Queries SQL usadas
- Configuração de produção
- Escalabilidade

Veja: [DOCUMENTACAO_SISTEMA.md](DOCUMENTACAO_SISTEMA.md)

## 📈 Próximos Passos

1. ✅ Setup local funcionando?
2. ✅ Dados aparecendo no dashboard?
3. → Deploy no Render
4. → Configurar domínio customizado (opcional)
5. → Configurar monitoramento/alertas (opcional)

## 📝 Notas de Versão

**v1.0** (13/08/2026)
- Sistema completo de dashboard em tempo real
- Suporte a 15 lojas
- Cache local para resiliência
- Deploy automático no Render
- Variáveis de ambiente para segurança

---

**Desenvolvido para**: Supermercados Vitória
**Status**: Production Ready
**Última atualização**: 13/08/2026
python app.py
```

Depois abra no navegador:

```text
http://127.0.0.1:5000/
```

O servidor fornece a interface e a API pelo mesmo endereço.

## Atualização dos dados

- Os indicadores e gráficos são atualizados automaticamente a cada **5 segundos**.
- Os dados são consultados diretamente no DB2.
- O dashboard evita requisições simultâneas.
- Se o banco estiver indisponível, a interface sinaliza o estado offline e usa o comportamento de fallback configurado no backend.

## Arquivos necessários

Mantenha estes arquivos juntos na mesma pasta:

- `app.py`
- `app.js`
- `index.html`
- `style.css`
- `requirements.txt`

O arquivo `README.md` é apenas a documentação.

## Segurança

As credenciais do banco estão sendo usadas pelo backend. Não publique o `app.py` em repositórios públicos nem compartilhe as credenciais em mensagens ou documentos externos.

Para produção, o ideal é mover usuário, senha e demais configurações para variáveis de ambiente.

## Problemas comuns

### `No module named ibm_db`

Execute novamente:

```powershell
python -m pip install -r requirements.txt
```

### A API retorna erro de conexão

Verifique host, porta, usuário, senha, firewall e permissões do DB2.

### A tela não atualiza

Confirme que o servidor está rodando e abra:

```text
http://127.0.0.1:5000/
```

Não abra apenas o `index.html` diretamente pelo explorador de arquivos, pois a API precisa ser servida pelo Flask.

### Gráficos sem carregar

O navegador precisa conseguir acessar a internet para carregar o ApexCharts pelo CDN. Se a rede bloquear o CDN, a biblioteca deverá ser baixada e servida localmente.
