# 📊 DOCUMENTAÇÃO COMPLETA - DASHBOARD FINANCEIRO DE VENDAS

## 1. VISÃO GERAL DO SISTEMA

### Intuito
Este é um **Dashboard de Vendas em Tempo Real** que monitora e exibe métricas financeiras de uma rede de lojas de supermercados. O sistema foi desenvolvido para fornecer visualização instantânea de:
- Vendas por hora do dia
- Faturamento por loja
- Faturamento acumulado do mês
- KPIs financeiros (ticket médio, horário de pico, margem de lucro, etc.)

### Tipo de Aplicação
- **Frontend**: Aplicação web monopágina (SPA) em HTML5 + JavaScript vanilla
- **Backend**: API REST em Python (Flask)
- **Banco de Dados**: IBM DB2 (banco de dados comercial)
- **Gráficos**: ApexCharts (biblioteca de visualização de dados)

---

## 2. ARQUITETURA GERAL

```
┌─────────────────────────────────────────────────────────────┐
│                        NAVEGADOR (Browser)                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              FRONTEND (HTML + CSS + JS)                │ │
│  │  - index.html: Estrutura HTML                         │ │
│  │  - style.css: Estilos e design                        │ │
│  │  - app.js: Lógica de atualização e gráficos           │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────┬─────────────────────────────────────────┘
                     │ Requisições HTTP (CORS enabled)
                     │ GET /api/dashboard
                     │ GET /cache_vendas.json
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (Flask / Python)                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              app.py (Servidor de API)                 │ │
│  │  - Rota /api/dashboard: Query ao DB2                  │ │
│  │  - Sistema de cache em JSON                           │ │
│  │  - Tratamento de erros                                │ │
│  │  - CORS habilitado                                    │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────┬─────────────────────────────────────────┘
                     │ Conexão TCP/IP porta 50022
                     ↓
┌─────────────────────────────────────────────────────────────┐
│          IBM DB2 (Database Server Remoto)                    │
│  Host: SUPERMERCADOSVITORIADB.DATACISS.COM.BR               │
│  Database: VITORIA                                           │
│  Tabelas principais:                                         │
│    - DBA.NOTAS: Dados das notas fiscais                      │
│    - DBA.NOTAS_ENTRADA_SAIDA: Tipo de movimento             │
│    - DBA.ESTOQUE_ANALITICO: Dados de vendas e lucro         │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. COMPONENTES DO FRONTEND (app.js)

### 3.1 Inicialização
```javascript
document.addEventListener("DOMContentLoaded", () => {
  // Executa quando a página está completamente carregada
})
```

### 3.2 Configurações Principais
- **API_BASE_URL**: URL da API (detecta automaticamente em produção ou usa localhost)
- **HORA_INICIO**: 6 (horário de abertura das lojas)
- **HORA_FIM**: 22 (horário de fechamento)
- **atualizacaoEmAndamento**: Flag que previne múltiplas requisições simultâneas

### 3.3 Funções Principais

#### `getOperatingHours()`
```javascript
const getOperatingHours = () => {
  const horaAtual = new Date().getHours();
  const horaLimite = Math.min(Math.max(horaAtual, HORA_INICIO), HORA_FIM);
  return Array.from(
    { length: horaLimite - HORA_INICIO + 1 },
    (_, indice) => HORA_INICIO + indice
  );
};
```
**Propósito**: Calcula quais horas devem ser exibidas no gráfico (apenas horário comercial)
**Retorno**: Array com as horas de 6 até a hora atual (ex: [6, 7, 8, 9, 10])

#### `getVisibleChartData(values)`
**Propósito**: Filtra dados para mostrar apenas o horário de funcionamento
**Entrada**: Array com 24 posições (horas 0-23)
**Saída**: 
```javascript
{
  categorias: ["06h", "07h", "08h", ...],
  valores: [valor_h6, valor_h7, valor_h8, ...]
}
```

#### `updateClock()`
**Propósito**: Atualiza o relógio em tempo real no canto superior direito
**Frequência**: A cada 1 segundo
**Formato**: HH:MM:SS

#### `atualizarDashboard()`
**Propósito**: Faz requisição à API para obter dados atualizados
**Frequência**: A cada 2 segundos (nova tentativa)
**Timeout**: 5 segundos por requisição

**Fluxo**:
1. Verifica se já existe uma atualização em andamento
2. Se sim, cancela e aguarda próxima tentativa
3. Se não, faz requisição GET para `/api/dashboard`
4. Se conseguir dados: aplica ao dashboard
5. Se falhar: tenta carregar do cache local (cache_vendas.json)
6. Se tudo falhar: exibe status "OFFLINE"

#### `applyDashboardData(dados)`
**Propósito**: Atualiza todos os elementos visuais com os dados recebidos
**Atualiza**:
- Cards de KPIs (total vendido, horário de pico, transações, ticket médio, margem de lucro)
- Gráfico de linha (vendas por hora)
- Gráfico de barras (faturamento por loja - hoje)
- Gráfico de barras (faturamento por loja - mês)
- Status da conexão (AO VIVO / CACHE / OFFLINE)

### 3.4 Gráficos (ApexCharts)

#### Gráfico 1: Receita por Hora (Linha)
```javascript
chart = new ApexCharts(chartContainer, {
  type: "line",           // Gráfico de linhas
  height: 400,
  series: [{name: "Receita", data: []}],
  colors: ["#3b82f6"],    // Azul
  xaxis: {categories: horas}, // Eixo X: 06h, 07h, 08h, ...
  yaxis: {
    min: 0,
    max: 200000,
    formatter: (val) => `R$${(val/1000).toFixed(1)}k` // Formato: R$50.0k
  }
})
```
**Dados exibidos**: Valores de venda da hora 6 até hora atual
**Atualização**: Cada requisição bem-sucedida

#### Gráfico 2 e 3: Faturamento por Loja (Barras Horizontais)
```javascript
companyChart = new ApexCharts(companyChartContainer, {
  type: "bar",
  plotOptions: {
    bar: {
      horizontal: true,     // Barras horizontais
      position: "end",      // Rótulos ao final da barra
      offsetX: 12           // Espaçamento do rótulo
    }
  },
  series: [{name: "Faturamento", data: []}]
})
```
**Diferença entre os dois**:
- Gráfico 2: Vendas de **HOJE** por loja
- Gráfico 3: Vendas **ACUMULADAS DO MÊS** por loja

---

## 4. COMPONENTES DO BACKEND (app.py)

### 4.1 Configuração Flask
```python
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response
```
**CORS**: Permite requisições do navegador de qualquer origem
**Cache-Control**: Desabilita cache do browser para sempre obter dados frescos

### 4.2 Configurações de Conexão ao DB2
```python
HOST = "SUPERMERCADOSVITORIADB.DATACISS.COM.BR"
PORT = "50022"
DATABASE = "VITORIA"
USERNAME = "USERNAME-ESCONDIDO"
PASSWORD = "SENHA-ESCONDIDA"
CACHE_FILE = "cache_vendas.json"
TTL_SECONDS = 0  # Cache sempre valido (não expira)
```

### 4.3 Dicionário de Empresas (Lojas)
```python
EMPRESAS = {
    3: "Torquato",
    4: "Grande Circular",
    5: "São José",
    6: "Coroado",
    7: "Centro",
    8: "Turismo",
    9: "Japiim",
    10: "Cidade de Deus",
    11: "Autaz Mirim",
    12: "Galileia",
    13: "Vierialves",
    14: "Jacira Reis",
    15: "Ponta Negra",
}
```
Mapeamento de IDs do banco para nomes legíveis

### 4.4 Funções Utilitárias

#### `format_currency(valor)`
Formata números para formato de moeda brasileira
- Entrada: `123456.78`
- Saída: `R$ 123.456,78`

#### `parse_db_number(valor)`
Converte strings/números do DB2 para float
- Trata valores None
- Converte strings com decimais brasileiros (vírgula)

#### `load_cache()` e `save_cache()`
Gerencia arquivo JSON local para cache de dados
- Usado quando API/DB falha
- Sempre entrega dados mais recentes possíveis

### 4.5 Rotas HTTP

#### Rota 1: `/` (Servir HTML)
```python
@app.route("/")
def index():
    return send_file("index.html")
```

#### Rota 2: `/api/dashboard` (Principal)
```python
@app.route("/api/dashboard")
def dashboard():
```

**Método**: GET
**Parâmetros Query**: Nenhum (usa `?ts` apenas para invalidar cache)

**Processo**:

1. **Verifica disponibilidade do driver IBM DB2**
   - Se indisponível, retorna cache ou erro

2. **Estabelece conexão com DB2**
   - TCP/IP na porta 50022
   - Credenciais pré-configuradas
   - Se falhar, retorna cache

3. **Executa 3 queries principais**:

##### Query 1: Vendas por Hora (Últimas 24h)
```sql
SELECT HOUR(NOTAS.DTMOVIMENTO) AS HORA,
       SUM(...) AS TOTALVENDA,
       COUNT(...) AS QTDCLIENTES
FROM DBA.NOTAS
INNER JOIN DBA.NOTAS_ENTRADA_SAIDA
INNER JOIN DBA.ESTOQUE_ANALITICO
WHERE NOTAS.FLAGNOTACANCEL = 'F'  -- Apenas notas não canceladas
  AND NOTAS_ENTRADA_SAIDA.TIPOMOVIMENTO IN ('V', 'E')  -- Venda ou Entrada
  AND ESTOQUE_ANALITICO.IDOPERACAO <> 1301  -- Exclui ajustes
  AND ((data HOJE) OR (data ONTEM))  -- Últimas 24h
GROUP BY HORA
```
**Retorna**: Vendas por hora de hoje E ontem (para cálculo de variação)

##### Query 2: Faturamento por Loja (Hoje)
```sql
SELECT ESTOQUE_ANALITICO.IDEMPRESA AS IDEMPRESA,
       SUM(...) AS TOTAL_VENDA
FROM DBA.NOTAS
WHERE NOTAS.FLAGNOTACANCEL = 'F'
  AND ... (mesmos filtros)
  AND ESTOQUE_ANALITICO.DTMOVIMENTO >= hoje
  AND ESTOQUE_ANALITICO.DTMOVIMENTO < amanhã
GROUP BY IDEMPRESA
ORDER BY TOTAL_VENDA DESC
```
**Retorna**: Total de vendas de cada loja **hoje**

##### Query 3: Faturamento por Loja (Mês Atual)
```sql
SELECT IDEMPRESA, SUM(VALTOTLIQUIDO) AS TOTAL_VENDA
FROM ...
WHERE ... (mesmos filtros)
  AND DTMOVIMENTO >= primeiro_dia_mes
  AND DTMOVIMENTO < primeiro_dia_proximo_mes
GROUP BY IDEMPRESA
```
**Retorna**: Total acumulado do mês por loja

##### Query 4: Margem de Lucro (Bônus)
```sql
SELECT SUM(ESTOQUE_ANALITICO.VALLUCRO) AS TOTAL_LUCRO,
       SUM(ESTOQUE_ANALITICO.VALTOTLIQUIDO) AS TOTAL_VENDA
FROM ... (mesmos filtros, hoje)
```
**Retorna**: Lucro total / Venda total = % Margem de Lucro

4. **Processa dados**:
   - Agrupa vendas por hora
   - Identifica horário de pico (maior valor)
   - Calcula ticket médio = total_vendido / transações
   - Calcula variação vs ontem = (hoje - ontem) / ontem * 100%
   - Ordena lojas por venda (maior para menor)

5. **Estrutura resposta JSON**:
```json
{
  "status": "success",
  "timestamp": "14:32:45",
  "kpis": {
    "total_vendido": "R$ 125.432,50",
    "horario_pico": "14:00 (R$ 12.543,00)",
    "transacoes": "1.234",
    "ticket_medio": "R$ 102,00",
    "margem_lucro": "↑ 28.5%",
    "comparativo": "↑ 15.3% vs. ontem",
    "total_vendido_mes_atual": "R$ 2.543.210,00",
    "total_vendido_mes_anterior": "R$ 2.234.123,00"
  },
  "grafico": {
    "categorias": ["06h", "07h", ..., "14h"],
    "valores": [1000.00, 1500.00, ..., 12543.00]
  },
  "empresas": [
    {"id": 6, "nome": "Coroado", "valor": 45000.00},
    {"id": 3, "nome": "Torquato", "valor": 42000.00},
    ...
  ],
  "empresas_mes": [
    {"id": 6, "nome": "Coroado", "valor": 850000.00},
    ...
  ]
}
```

**Tratamento de Erros**:
- Se DB2 não conecta → retorna cache + status "cache"
- Se SQL falha → retorna cache + mensagem de erro
- Se tudo falha → retorna payload vazio com status "error"

---

## 5. FLUXO DE DADOS EM TEMPO REAL

### Timeline de uma atualização:

```
T=0s      → Frontend chama atualizarDashboard()
          → Flag: atualizacaoEmAndamento = true

T=0s-5s   → Requisição HTTP GET /api/dashboard
          → Backend conecta ao DB2
          → Executa 4 queries SQL
          → Processa dados
          → Retorna JSON

T=5s      → Frontend recebe resposta
          → Atualiza todos os elementos DOM
          → Atualiza gráficos ApexCharts
          → Flag: atualizacaoEmAndamento = false

T=2s      → Próxima tentativa agendada (setInterval 2s)
          → Aguarda, pois atualizacaoEmAndamento = true

T=5s+     → Quando a atualização anterior termina
          → Imediatamente faz nova requisição

T=10s     → Repete o ciclo
```

### Intervalo Real de Atualização:
- **Intervalo de tentativa**: 2 segundos
- **Tempo de requisição**: ~5 segundos
- **Resultado**: Atualização efetiva a cada ~5-6 segundos
- **Razão**: A requisição leva ~5s, então enquanto processa, não faz nova requisição

---

## 6. SISTEMA DE CACHE

### Arquivo: `cache_vendas.json`

**Propósito**: Fornecer dados quando:
- Backend/DB2 indisponível
- Internet fora
- API demorando demais

**Estrutura**: Idêntica ao retorno da API

**Quando é atualizado**: 
- Após cada requisição bem-sucedida (`save_cache(resposta)`)

**Status exibido**:
- "AO VIVO" = dados direto do DB2
- "CACHE" = dados do arquivo local
- "OFFLINE" = nem API nem cache disponível

---

## 7. COMO COLOCAR EM PRODUÇÃO (Browser)

### Opção 1: Hospedagem em Servidor Web (RECOMENDADO)

#### Passo 1: Preparar Servidor
- Servidor Linux/Windows com Python 3.8+
- Porta 5000 (ou qualquer porta disponível)
- Acesso à rede onde está o DB2

#### Passo 2: Instalar Dependências Backend
```bash
pip install flask ibm-db
```

#### Passo 3: Configurar Firewall
- Permitir acesso na porta do Flask (5000)
- Permitir acesso TCP/IP ao DB2 (porta 50022)

#### Passo 4: Iniciar Backend
```bash
python app.py
```
Ou melhor, usar production server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Passo 5: Apontar Frontend
- Upload dos arquivos (index.html, app.js, style.css) para servidor web
- O `app.js` detecta automaticamente:
  ```javascript
  const API_BASE_URL =
    window.location.protocol.startsWith("http") && window.location.origin !== "null"
      ? window.location.origin  // Usa mesma URL da página
      : "http://127.0.0.1:5000"; // Usa localhost se não conseguir
  ```

#### Passo 6: Acessar
- Browser: `http://seu_servidor_ip:porta`
- Pronto! Dashboard funcionando em tempo real

### Opção 2: Servidor Web Separado (Nginx/Apache)
```nginx
server {
    listen 80;
    server_name seu_dominio.com;

    location / {
        root /var/www/dashboard;
        index index.html;
    }

    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Opção 3: Docker (Mais Robusto)

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

#### docker-compose.yml
```yaml
version: '3'
services:
  dashboard:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DB_HOST=SUPERMERCADOSVITORIADB.DATACISS.COM.BR
      - DB_PORT=50022
    volumes:
      - ./cache_vendas.json:/app/cache_vendas.json
```

---

## 8. REQUISITOS MÍNIMOS DE PRODUÇÃO

### Hardware
- CPU: 1-2 cores (suficiente para Flask)
- RAM: 512MB - 1GB
- Disco: 100MB (apenas arquivos)

### Software
- Python 3.8+
- Driver IBM DB2 (ibm-db)
- Flask 2.0+
- Gunicorn (production server)

### Rede
- Acesso às lojas (ou via VPN)
- Conexão estável ao DB2
- Latência baixa recomendada (<100ms)

### Segurança
- HTTPS em produção (certificado SSL)
- Proxy reverso (Nginx/Apache)
- Firewall restringindo acesso ao banco
- Não expor credenciais do DB2 no cliente

---

## 9. SITUAÇÕES ESPECÍFICAS E TRATAMENTO

### Situação 1: API Demorando (5+ segundos)
**O que acontece**:
- Requisição é cancelada após 5s
- Próxima tentativa em 2s
- Usa cache enquanto aguarda

**Solução**:
- Otimizar queries SQL
- Aumentar `timeout` em `app.js` linha 297
- Adicionar índices no DB2

### Situação 2: DB2 Indisponível
**O que acontece**:
- Primeira tentativa falha
- Segunda tentativa tenta carregar `cache_vendas.json`
- Se bem-sucedido: exibe "● CACHE"
- Dashboard fica com dados desatualizados mas funcional

### Situação 3: Múltiplas requisições simultâneas
**O que acontece**:
- Flag `atualizacaoEmAndamento` previne
- Requisições extras são ignoradas
- Evita sobrecarga

### Situação 4: Primeiro acesso
**O que acontece**:
- Cards mostram "Carregando..."
- Gráficos vazios
- Após primeira requisição bem-sucedida, popula dados
- Relógio atualiza cada segundo

### Situação 5: Conexão perdida durante dashboard aberto
**O que acontece**:
- Status muda para "● OFFLINE"
- Cards limpam
- Continua tentando a cada 2s
- Quando reconecta, dados aparecem novamente

---

## 10. ESTRUTURA DE ARQUIVOS EM PRODUÇÃO

```
/dashboard-vendas/
├── app.py                      # Servidor Backend (Flask)
├── requirements.txt            # Dependências Python
├── index.html                  # Página principal
├── app.js                      # Lógica Frontend
├── style.css                   # Estilos
├── cache_vendas.json          # Cache local (autogenerado)
├── README.md                   # Documentação
├── DOCUMENTACAO_SISTEMA.md     # Esta documentação
├── Dockerfile                  # Para containerização
└── docker-compose.yml          # Orquestração
```

---

## 11. RESUMO TÉCNICO PARA DEPLOY

**Stack**: Python Flask + Vanilla JS + IBM DB2
**Comunicação**: HTTP REST + JSON
**Atualização**: Long-polling a cada 2-5 segundos
**Cache**: JSON local para fallback
**Escalabilidade**: Gunicorn multi-worker + Nginx reverse proxy
**Segurança**: CORS + HTTPS (em produção) + Autenticação (optional)

**Para colocar online**:
1. Upload arquivos para servidor
2. Instalar Python + dependências
3. Executar `python app.py` ou `gunicorn`
4. Configurar proxy reverso (Nginx/Apache)
5. Acessar via browser
6. Pronto! ✅

---

**Última atualização**: 13/08/2026
**Versão**: 1.0
**Status**: Produção
