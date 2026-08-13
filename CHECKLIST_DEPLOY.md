# ✅ CHECKLIST PRÉ-DEPLOY

Use este checklist para garantir que tudo está pronto para GitHub e Render.

## 📋 Arquivos Necessários

### Backend
- [ ] `app.py` - ✅ Credenciais agora usam variáveis de ambiente
- [ ] `requirements.txt` - ✅ Contém Flask, ibm_db, gunicorn, python-dotenv
- [ ] `Procfile` - ✅ Com comando `web: gunicorn app:app`

### Frontend
- [ ] `index.html` - ✅ Página principal
- [ ] `app.js` - ✅ Lógica JavaScript
- [ ] `style.css` - ✅ Estilos CSS

### Configuração
- [ ] `.env.example` - ✅ Modelo de variáveis (sem valores reais)
- [ ] `.gitignore` - ✅ Protege `.env` de ser commitado

### Documentação
- [ ] `README.md` - ✅ Instruções de setup
- [ ] `DOCUMENTACAO_SISTEMA.md` - ✅ Documentação técnica
- [ ] `DEPLOY_RENDER.md` - ✅ Guia passo-a-passo Render

### Cache (Gerado automaticamente)
- [ ] `cache_vendas.json` - Será criado na primeira execução

---

## 🔒 Segurança

### .env
- [ ] `.env` existe com credenciais reais (não commitado)
- [ ] `.env.example` existe como modelo (commitado)
- [ ] `.gitignore` contém `.env`

### app.py
- [ ] Está usando `os.getenv()` para ler variáveis
- [ ] Não contém mais credenciais hardcoded
- [ ] Importa `from dotenv import load_dotenv`

### GitHub
- [ ] `.env` **NÃO** está no repositório
- [ ] Credenciais **NÃO** aparecem em commits
- [ ] Repositório é **privado** (recomendado)

---

## 🚀 Render

### Variáveis de Ambiente no Render
- [ ] `DB_HOST` configurado
- [ ] `DB_PORT` configurado
- [ ] `DB_NAME` configurado
- [ ] `DB_USER` configurado
- [ ] `DB_PASSWORD` configurado
- [ ] `FLASK_ENV` = `production`

### Build
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `gunicorn app:app`
- [ ] Python 3 selecionado

---

## ✨ Funcionalidades

### Frontend
- [ ] Gráfico de linhas (Receita por Hora) - linha 297
- [ ] Gráfico de barras (Faturamento por Loja) - linha 165
- [ ] Gráfico de barras (Faturamento Mês) - linha 225
- [ ] Cards de KPIs aparecem
- [ ] Relógio atualiza a cada segundo
- [ ] Status da API mostra status (AO VIVO / CACHE / OFFLINE)

### Backend
- [ ] Rota `/` - Serve HTML
- [ ] Rota `/api/dashboard` - Retorna dados JSON
- [ ] CORS habilitado para requisições do navegador
- [ ] Cache local funciona se DB falhar
- [ ] Timeout de 5s nas requisições

### Atualizações
- [ ] Dados atualizam a cada ~5 segundos
- [ ] Intervalo entre tentativas: 2 segundos
- [ ] Timeout da requisição: 5 segundos
- [ ] Flag `atualizacaoEmAndamento` previne requisições simultâneas

---

## 🧪 Testes Locais

### Antes de fazer commit:
```bash
# 1. Criar .env com credenciais reais
cp .env.example .env
# Editar .env com seus valores

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar servidor
python app.py

# 4. Testar no navegador
# Abrir http://localhost:5000
# Confirmar que dados aparecem
# Abrir DevTools (F12) → Network
# Confirmar que /api/dashboard retorna JSON
```

### Testes de Git:
```bash
# 1. Verificar se .env está ignorado
git status | grep ".env"
# Não deve aparecer nada

# 2. Verificar se credenciais vazaram
git log --all --source --full-history -- app.py | grep -i password
# Não deve aparecer nada

# 3. Listar arquivos que serão commitados
git status
# Não deve conter .env
# Deve conter: app.py, index.html, app.js, style.css, etc.
```

---

## 📦 Estrutura Final no GitHub

```
dashboard-vendas/
├── app.py                      ✅
├── index.html                  ✅
├── app.js                      ✅
├── style.css                   ✅
├── requirements.txt            ✅
├── Procfile                    ✅
├── .env.example                ✅
├── .gitignore                  ✅
├── README.md                   ✅
├── DOCUMENTACAO_SISTEMA.md     ✅
└── DEPLOY_RENDER.md            ✅

NÃO COMMITADO:
├── .env                        ❌ (está no .gitignore)
├── cache_vendas.json          ❌ (será gerado)
└── __pycache__/               ❌ (está no .gitignore)
```

---

## 🎯 Passos Finais

### 1. Preparar
```bash
# Copiar arquivo .env.example para .env
cp .env.example .env

# Editar .env com credenciais reais
# (use seu editor favorito)
```

### 2. Testar Localmente
```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
python app.py

# Abrir browser: http://localhost:5000
# Confirmar que funciona
```

### 3. Git Commit
```bash
# Adicionar arquivos
git add app.py index.html app.js style.css
git add requirements.txt Procfile .gitignore .env.example
git add README.md DOCUMENTACAO_SISTEMA.md DEPLOY_RENDER.md

# Confirmar (sem .env!)
git status

# Commit
git commit -m "Dashboard Vendas para GitHub e Render"

# Push
git push origin main
```

### 4. Deploy Render
- Seguir [DEPLOY_RENDER.md](DEPLOY_RENDER.md)
- Adicionar variáveis de ambiente no Render
- Confirmar que está live

### 5. Testar em Produção
```bash
# Acessar URL do Render
https://dashboard-vendas.onrender.com

# Confirmar que:
# - Dashboard carrega
# - Dados aparecem
# - Status mostra "AO VIVO" (não cache)
# - Gráficos atualizam
```

---

## 🆘 Se Algo Der Errado

### "No module named dotenv"
```bash
pip install python-dotenv
```

### "Connection refused" ao DB2
- Render não pode acessar DB2 remoto (firewall)
- Solução: Usar VPN ou DB2 em rede acessível

### Variáveis de ambiente não funcionam
- Confirmar que foram adicionadas no Render
- Reiniciar serviço no Render
- Verificar nomes das variáveis (case-sensitive)

### Credenciais vazadas no GitHub
```bash
# Usar git-filter-branch para remover
git filter-branch -f --prune-empty --index-filter 'git rm -rf --cached --ignore-unmatch .env' -- --all
git push origin --force-with-lease
```

---

**Data**: 13/08/2026
**Versão**: 1.0
**Status**: Ready for Deployment ✅

Qualquer dúvida, veja [DOCUMENTACAO_SISTEMA.md](DOCUMENTACAO_SISTEMA.md)
