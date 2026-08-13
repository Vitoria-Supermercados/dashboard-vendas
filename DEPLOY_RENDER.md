# 🚀 GUIA RÁPIDO: GitHub → Render

## 1. Preparar GitHub

### Passo 1: Clonar/criar repositório
```bash
# Se já existe
cd seu_projeto

# Se é novo
mkdir dashboard-vendas
cd dashboard-vendas
git init
```

### Passo 2: Adicionar arquivos ao Git
```bash
git add app.py index.html app.js style.css
git add requirements.txt Procfile .gitignore .env.example
git add DOCUMENTACAO_SISTEMA.md README.md

git commit -m "Projeto Dashboard Vendas para Render"
git push origin main
```

### ⚠️ IMPORTANTE: Nunca commit `.env`
O arquivo `.gitignore` já protege isso. Confirme:
```bash
cat .gitignore | grep ".env"
```

Deve aparecer:
```
.env
.env.local
```

---

## 2. Deploy no Render

### Passo 1: Criar conta (se não tiver)
- Vá para [render.com](https://render.com)
- Clique em "Sign up"
- Use sua conta GitHub (mais fácil)

### Passo 2: Criar novo Web Service
1. Dashboard → Clique em **"New +"**
2. Selecione **"Web Service"**
3. Clique em **"Connect a repository"**
4. Selecione seu repositório `dashboard-vendas`

### Passo 3: Configurar Build
Preencha assim:

```
Name:                dashboard-vendas
Environment:         Python 3
Build Command:       pip install -r requirements.txt
Start Command:       gunicorn app:app
Region:             São Paulo (ou sua região)
Instance Type:       Free (começa com free)
```

### Passo 4: Adicionar Variáveis de Ambiente
1. Clique na aba **"Environment"**
2. Adicione cada variável:

```
DB_HOST              SUPERMERCADOSVITORIADB.DATACISS.COM.BR
DB_PORT              50022
DB_NAME              VITORIA
DB_USER              vitoria
DB_PASSWORD          sua_senha_aqui (será criptografada)
FLASK_ENV            production
```

### Passo 5: Deploy
1. Clique em **"Create Web Service"**
2. Render faz o build automaticamente
3. Quando ficar **VERDE ✓**, está pronto!
4. URL: `https://dashboard-vendas.onrender.com`

---

## 3. Atualizações Futuras

Qualquer commit que você fazer no `main`:
```bash
git add .
git commit -m "Descrição da alteração"
git push origin main
```

O Render detecta e faz redeploy automaticamente!

---

## 4. Troubleshooting no Render

### Erro no Build
- Clique em **"Logs"**
- Procure por mensagens de erro
- Verifique se `requirements.txt` está correto

### API retorna 500
- Clique em **"Logs"**
- Procure por "Connection refused" ou erros de DB2
- Verifique credenciais no "Environment"

### Dashboard vazio
- Abra DevTools (F12) → Console
- Verifique se há erros CORS
- Confirme se backend está respondendo

### Precisa de mais RAM
- Mude para plano "Starter" ($7/mês)
- Render avisa se precisar

---

## 5. Monitoring

### Ver logs ao vivo
```bash
render logs dashboard-vendas
```

### Health Check
Render faz ping automático em:
```
https://dashboard-vendas.onrender.com/
```

Se parar de responder, recria automaticamente.

---

## 6. Custom Domain (Opcional)

Se tiver domínio próprio:
1. Vá para **"Settings"** do serviço
2. Clique em **"Add Custom Domain"**
3. Aponte o DNS do seu domínio para Render

Exemplo:
```
seu_dominio.com → dashboard-vendas.onrender.com
```

---

## 7. Backup de Dados

O `cache_vendas.json` é gerado automaticamente.
Se precisar fazer backup:

```bash
curl https://dashboard-vendas.onrender.com/cache_vendas.json > backup.json
```

---

## Resumo de Arquivos Necessários

✅ `app.py` - Backend
✅ `index.html` - Frontend
✅ `app.js` - Lógica
✅ `style.css` - Estilos
✅ `requirements.txt` - Dependências (OBRIGATÓRIO)
✅ `Procfile` - Instruções Render (OBRIGATÓRIO)
✅ `.env.example` - Modelo (sem valores)
✅ `.gitignore` - Protege .env
✅ `README.md` - Documentação
✅ `DOCUMENTACAO_SISTEMA.md` - Documentação técnica

❌ `.env` - NUNCA commit! (variáveis no Render)
❌ `cache_vendas.json` - Gerado automaticamente

---

**Pronto! Dashboard no ar! 🎉**

Qualquer dúvida, consulte [DOCUMENTACAO_SISTEMA.md](DOCUMENTACAO_SISTEMA.md)
