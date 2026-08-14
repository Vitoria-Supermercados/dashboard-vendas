import json
import logging
import os
import threading
import signal
import time
from datetime import datetime, timedelta
from typing import Any

from flask import Flask, jsonify, request, send_file
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

try:
    import ibm_db
except Exception as exc:
    ibm_db = None
    IBM_DB_IMPORT_ERROR = exc
else:
    IBM_DB_IMPORT_ERROR = None

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

# Lê credenciais do arquivo .env (ou variáveis de ambiente)
HOST = os.getenv("DB_HOST", "SUPERMERCADOSVITORIADB.DATACISS.COM.BR")
PORT = os.getenv("DB_PORT", "50022")
DATABASE = os.getenv("DB_NAME", "VITORIA")
USERNAME = os.getenv("DB_USER", "vitoria")
PASSWORD = os.getenv("DB_PASSWORD", "")
CACHE_FILE = os.path.join(os.path.dirname(__file__), "cache_vendas.json")
CACHE_TTL_SECONDS = 10
TTL_SECONDS = 0
REFRESH_IN_PROGRESS = False
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


def format_currency(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_db_number(valor: Any) -> float:
    if valor is None:
        return 0.0
    if isinstance(valor, str):
        valor = valor.strip()
        if "," in valor:
            valor = valor.replace(".", "").replace(",", ".")
    return float(valor)


def connect_db_with_timeout(conn_str: str, timeout_seconds: int = 10):
    """Tenta conectar ao DB2 com timeout definido."""
    connection = [None]
    error = [None]
    
    def connect_thread():
        try:
            connection[0] = ibm_db.connect(conn_str, "", "")
        except Exception as e:
            error[0] = e
    
    thread = threading.Thread(target=connect_thread, daemon=True)
    thread.start()
    thread.join(timeout=timeout_seconds)
    
    if thread.is_alive():
        raise TimeoutError(f"Conexão ao DB2 expirou após {timeout_seconds} segundos")
    
    if error[0]:
        raise error[0]
    
    if connection[0] is None:
        raise Exception("Conexão ao DB2 retornou None")
    
    return connection[0]


def load_cache() -> dict[str, Any] | None:
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def save_cache(payload: dict[str, Any]) -> None:
    payload["cached_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)


def cache_is_fresh() -> bool:
    if not os.path.exists(CACHE_FILE):
        return False
    try:
        age_seconds = time.time() - os.path.getmtime(CACHE_FILE)
        return age_seconds <= CACHE_TTL_SECONDS
    except OSError:
        return False


def build_empty_payload() -> dict[str, Any]:
    return {
        "status": "error",
        "message": "Falha ao consultar o banco de dados.",
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "kpis": {
            "total_vendido": "R$ 0,00",
            "horario_pico": "00:00",
            "transacoes": "0",
            "ticket_medio": "R$ 0,00",
            "comparativo": "N/D",
            "margem_lucro": "N/D",
            "total_vendido_mes_atual": "R$ 0,00",
            "total_vendido_mes_anterior": "R$ 0,00",
        },
        "grafico": {
            "categorias": [f"{h:02d}h" for h in range(24)],
            "valores": [0.0 for _ in range(24)],
        },
    }


def build_error_payload(message: str) -> dict[str, Any]:
    payload = build_empty_payload()
    payload["message"] = message
    return payload


@app.route("/")
@app.route("/index.html")
def index():
    return send_file(os.path.join(os.path.dirname(__file__), "index.html"), mimetype="text/html")


@app.route("/style.css")
def style_css():
    return send_file(os.path.join(os.path.dirname(__file__), "style.css"), mimetype="text/css")


@app.route("/app.js")
def app_js():
    response = send_file(os.path.join(os.path.dirname(__file__), "app.js"), mimetype="application/javascript")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


@app.route("/cache_vendas.json")
def cache_vendas():
    return send_file(os.path.join(os.path.dirname(__file__), "cache_vendas.json"), mimetype="application/json")


@app.route("/api/dashboard")
def dashboard():
    if request.method == "OPTIONS":
        return "", 200

    global REFRESH_IN_PROGRESS

    cache = load_cache()
    if cache and cache_is_fresh():
        cache["status"] = "cache"
        cache["message"] = "Dados em cache: atualizado há menos de 30 segundos."
        return jsonify(cache)

    if REFRESH_IN_PROGRESS:
        if cache:
            cache["status"] = "cache"
            cache["message"] = "Atualização já em andamento; servindo cache anterior."
            return jsonify(cache)
        return jsonify(build_empty_payload())

    if ibm_db is None:
        payload = build_empty_payload()
        payload["message"] = f"Driver IBM DB2 indisponível: {IBM_DB_IMPORT_ERROR}" if IBM_DB_IMPORT_ERROR else "Driver IBM DB2 indisponível."
        if cache:
            cache["status"] = "cache"
            return jsonify(cache)
        return jsonify(payload)

    REFRESH_IN_PROGRESS = True
    try:
        # Tenta conectar ao DB2 com timeout de 10 segundos
        conn_str = f"DATABASE={DATABASE};HOSTNAME={HOST};PORT={PORT};PROTOCOL=TCPIP;UID={USERNAME};PWD={PASSWORD};"
        conn = connect_db_with_timeout(conn_str, timeout_seconds=10)
    except Exception as exc:
        REFRESH_IN_PROGRESS = False
        message = f"Falha ao conectar ao banco: {exc}"
        logger.exception(message)
        if cache:
            cache["status"] = "cache"
            cache["message"] = message
            return jsonify(cache)
        return jsonify(build_error_payload(message))

    try:
        hoje = datetime.now().date()
        ontem = hoje - timedelta(days=1)
        dt_ini_1 = datetime.combine(hoje, datetime.min.time())
        dt_fim_1 = datetime.combine(hoje + timedelta(days=1), datetime.min.time())
        dt_ini_2 = datetime.combine(ontem, datetime.min.time())
        dt_fim_2 = datetime.combine(ontem + timedelta(days=1), datetime.min.time())

        dt_inicio_mes = datetime.combine(hoje.replace(day=1), datetime.min.time())
        if hoje.month == 12:
            dt_inicio_proximo_mes = datetime.combine(hoje.replace(year=hoje.year + 1, month=1, day=1), datetime.min.time())
        else:
            dt_inicio_proximo_mes = datetime.combine(hoje.replace(month=hoje.month + 1, day=1), datetime.min.time())

        if hoje.month == 1:
            dt_inicio_mes_anterior = datetime.combine(
                hoje.replace(year=hoje.year - 1, month=12, day=1), datetime.min.time()
            )
        else:
            dt_inicio_mes_anterior = datetime.combine(
                hoje.replace(month=hoje.month - 1, day=1), datetime.min.time()
            )
    except Exception as exc:
        REFRESH_IN_PROGRESS = False
        logger.exception("Erro ao preparar datas do dashboard: %s", exc)
        return jsonify(build_error_payload(f"Erro ao preparar datas do dashboard: {exc}"))

    sql_vendas = """
    SELECT TMP.HORA, SUM(TMP.TOTALVENDA) AS TOTALVENDA,
            COUNT(TMP.IDPLANILHA) AS QTDCLIENTES, TMP.PERIODO
    FROM (
        SELECT NOTAS.IDEMPRESA, NOTAS.IDPLANILHA,
               HOUR(NOTAS.DTMOVIMENTO) AS HORA,
               SUM(CASE WHEN NOTAS_ENTRADA_SAIDA.TIPOMOVIMENTO = 'E' THEN
                   ESTOQUE_ANALITICO.VALTOTLIQUIDO * (-1)
                   ELSE ESTOQUE_ANALITICO.VALTOTLIQUIDO END) AS TOTALVENDA,
               CASE WHEN ESTOQUE_ANALITICO.DTMOVIMENTO >= ? AND ESTOQUE_ANALITICO.DTMOVIMENTO < ?
                    THEN 'A' ELSE 'B' END AS PERIODO
        FROM DBA.NOTAS AS NOTAS
        INNER JOIN DBA.NOTAS_ENTRADA_SAIDA AS NOTAS_ENTRADA_SAIDA
            ON NOTAS.IDEMPRESA = NOTAS_ENTRADA_SAIDA.IDEMPRESA
           AND NOTAS.IDPLANILHA = NOTAS_ENTRADA_SAIDA.IDPLANILHA
        INNER JOIN DBA.ESTOQUE_ANALITICO AS ESTOQUE_ANALITICO
            ON NOTAS_ENTRADA_SAIDA.IDEMPRESA = ESTOQUE_ANALITICO.IDEMPRESA
           AND NOTAS_ENTRADA_SAIDA.IDPLANILHA = ESTOQUE_ANALITICO.IDPLANILHA
           AND NOTAS_ENTRADA_SAIDA.DTMOVIMENTO = ESTOQUE_ANALITICO.DTMOVIMENTO
        WHERE NOTAS.FLAGNOTACANCEL = 'F'
          AND NOTAS_ENTRADA_SAIDA.FLAGMOVPRODUTOS = 'T'
          AND (ESTOQUE_ANALITICO.NUMSEQUENCIAKIT IS NULL OR ESTOQUE_ANALITICO.NUMSEQUENCIAKIT <= 0)
          AND NOTAS_ENTRADA_SAIDA.TIPOMOVIMENTO IN ('V', 'E')
          AND ESTOQUE_ANALITICO.IDOPERACAO <> 1301
                    AND ((ESTOQUE_ANALITICO.DTMOVIMENTO >= ? AND ESTOQUE_ANALITICO.DTMOVIMENTO < ?)
                        OR (ESTOQUE_ANALITICO.DTMOVIMENTO >= ? AND ESTOQUE_ANALITICO.DTMOVIMENTO < ?))
        GROUP BY NOTAS.IDEMPRESA, NOTAS.IDPLANILHA,
                 HOUR(NOTAS.DTMOVIMENTO), ESTOQUE_ANALITICO.DTMOVIMENTO
    ) AS TMP
    GROUP BY TMP.HORA, TMP.PERIODO
    ORDER BY TMP.PERIODO, TMP.HORA
    """

    sql_empresas = """
        SELECT ESTOQUE_ANALITICO.IDEMPRESA AS IDEMPRESA,
                     SUM(CASE WHEN NOTAS_ENTRADA_SAIDA.TIPOMOVIMENTO = 'E' THEN
                             ESTOQUE_ANALITICO.VALTOTLIQUIDO * (-1)
                             ELSE ESTOQUE_ANALITICO.VALTOTLIQUIDO END) AS TOTAL_VENDA
        FROM DBA.NOTAS AS NOTAS
        INNER JOIN DBA.NOTAS_ENTRADA_SAIDA AS NOTAS_ENTRADA_SAIDA
                ON NOTAS.IDEMPRESA = NOTAS_ENTRADA_SAIDA.IDEMPRESA
             AND NOTAS.IDPLANILHA = NOTAS_ENTRADA_SAIDA.IDPLANILHA
        INNER JOIN DBA.ESTOQUE_ANALITICO AS ESTOQUE_ANALITICO
                ON NOTAS_ENTRADA_SAIDA.IDEMPRESA = ESTOQUE_ANALITICO.IDEMPRESA
             AND NOTAS_ENTRADA_SAIDA.IDPLANILHA = ESTOQUE_ANALITICO.IDPLANILHA
             AND NOTAS_ENTRADA_SAIDA.DTMOVIMENTO = ESTOQUE_ANALITICO.DTMOVIMENTO
        WHERE NOTAS.FLAGNOTACANCEL = 'F'
            AND NOTAS_ENTRADA_SAIDA.FLAGMOVPRODUTOS = 'T'
            AND (ESTOQUE_ANALITICO.NUMSEQUENCIAKIT IS NULL OR ESTOQUE_ANALITICO.NUMSEQUENCIAKIT <= 0)
            AND NOTAS_ENTRADA_SAIDA.TIPOMOVIMENTO IN ('V', 'E')
            AND ESTOQUE_ANALITICO.IDOPERACAO <> 1301
            AND ESTOQUE_ANALITICO.DTMOVIMENTO >= ?
            AND ESTOQUE_ANALITICO.DTMOVIMENTO < ?
        GROUP BY ESTOQUE_ANALITICO.IDEMPRESA
        ORDER BY TOTAL_VENDA DESC
        """

    sql_empresas_mes = """
        SELECT ESTOQUE_ANALITICO.IDEMPRESA AS IDEMPRESA,
                     SUM(CASE WHEN NOTAS_ENTRADA_SAIDA.TIPOMOVIMENTO = 'E' THEN
                             ESTOQUE_ANALITICO.VALTOTLIQUIDO * (-1)
                             ELSE ESTOQUE_ANALITICO.VALTOTLIQUIDO END) AS TOTAL_VENDA
        FROM DBA.NOTAS AS NOTAS
        INNER JOIN DBA.NOTAS_ENTRADA_SAIDA AS NOTAS_ENTRADA_SAIDA
                ON NOTAS.IDEMPRESA = NOTAS_ENTRADA_SAIDA.IDEMPRESA
             AND NOTAS.IDPLANILHA = NOTAS_ENTRADA_SAIDA.IDPLANILHA
        INNER JOIN DBA.ESTOQUE_ANALITICO AS ESTOQUE_ANALITICO
                ON NOTAS_ENTRADA_SAIDA.IDEMPRESA = ESTOQUE_ANALITICO.IDEMPRESA
             AND NOTAS_ENTRADA_SAIDA.IDPLANILHA = ESTOQUE_ANALITICO.IDPLANILHA
             AND NOTAS_ENTRADA_SAIDA.DTMOVIMENTO = ESTOQUE_ANALITICO.DTMOVIMENTO
        WHERE NOTAS.FLAGNOTACANCEL = 'F'
            AND NOTAS_ENTRADA_SAIDA.FLAGMOVPRODUTOS = 'T'
            AND (ESTOQUE_ANALITICO.NUMSEQUENCIAKIT IS NULL OR ESTOQUE_ANALITICO.NUMSEQUENCIAKIT <= 0)
            AND NOTAS_ENTRADA_SAIDA.TIPOMOVIMENTO IN ('V', 'E')
            AND ESTOQUE_ANALITICO.IDOPERACAO <> 1301
            AND ESTOQUE_ANALITICO.DTMOVIMENTO >= ?
            AND ESTOQUE_ANALITICO.DTMOVIMENTO < ?
        GROUP BY ESTOQUE_ANALITICO.IDEMPRESA
        ORDER BY TOTAL_VENDA DESC
        """

    try:
        stmt_vendas = ibm_db.prepare(conn, sql_vendas)
        ibm_db.execute(stmt_vendas, (dt_ini_1, dt_fim_1, dt_ini_1, dt_fim_1, dt_ini_2, dt_fim_2))
        linhas_vendas = []
        while ibm_db.fetch_row(stmt_vendas):
            linhas_vendas.append({
                "HORA_VENDA": ibm_db.result(stmt_vendas, 0),
                "TOTAL_VENDA": ibm_db.result(stmt_vendas, 1),
                "QTD_CLIENTES": ibm_db.result(stmt_vendas, 2),
                "PERIODO": ibm_db.result(stmt_vendas, 3),
            })

        stmt_empresas = ibm_db.prepare(conn, sql_empresas)
        ibm_db.execute(stmt_empresas, (dt_ini_1, dt_fim_1))
        linhas_empresas = []
        while ibm_db.fetch_row(stmt_empresas):
            linhas_empresas.append({
                "IDEMPRESA": ibm_db.result(stmt_empresas, 0),
                "TOTAL_VENDA": ibm_db.result(stmt_empresas, 1),
            })

        stmt_empresas_mes = ibm_db.prepare(conn, sql_empresas_mes)
        ibm_db.execute(stmt_empresas_mes, (dt_inicio_mes, dt_inicio_proximo_mes))
        linhas_empresas_mes = []
        while ibm_db.fetch_row(stmt_empresas_mes):
            linhas_empresas_mes.append({
                "IDEMPRESA": ibm_db.result(stmt_empresas_mes, 0),
                "TOTAL_VENDA": ibm_db.result(stmt_empresas_mes, 1),
            })

        total_vendido_mes_atual = sum(parse_db_number(linha["TOTAL_VENDA"]) for linha in linhas_empresas_mes)

        stmt_empresas_mes_anterior = ibm_db.prepare(conn, sql_empresas_mes)
        ibm_db.execute(stmt_empresas_mes_anterior, (dt_inicio_mes_anterior, dt_inicio_mes))
        total_vendido_mes_anterior = 0.0
        while ibm_db.fetch_row(stmt_empresas_mes_anterior):
            total_vendido_mes_anterior += parse_db_number(ibm_db.result(stmt_empresas_mes_anterior, 1))

        total_venda_lucro = 0.0
        total_lucro = 0.0
        margem_calculada = False
        try:
            sql_margem = """
                SELECT
                    SUM(ESTOQUE_ANALITICO.VALLUCRO) AS TOTAL_LUCRO,
                    SUM(ESTOQUE_ANALITICO.VALTOTLIQUIDO) AS TOTAL_VENDA
                FROM DBA.NOTAS AS NOTAS
                INNER JOIN DBA.NOTAS_ENTRADA_SAIDA AS NOTAS_ENTRADA_SAIDA
                    ON NOTAS.IDEMPRESA = NOTAS_ENTRADA_SAIDA.IDEMPRESA
                   AND NOTAS.IDPLANILHA = NOTAS_ENTRADA_SAIDA.IDPLANILHA
                INNER JOIN DBA.ESTOQUE_ANALITICO AS ESTOQUE_ANALITICO
                    ON NOTAS_ENTRADA_SAIDA.IDEMPRESA = ESTOQUE_ANALITICO.IDEMPRESA
                   AND NOTAS_ENTRADA_SAIDA.IDPLANILHA = ESTOQUE_ANALITICO.IDPLANILHA
                   AND NOTAS_ENTRADA_SAIDA.DTMOVIMENTO = ESTOQUE_ANALITICO.DTMOVIMENTO
                WHERE NOTAS.FLAGNOTACANCEL = 'F'
                  AND NOTAS_ENTRADA_SAIDA.FLAGMOVPRODUTOS = 'T'
                  AND (ESTOQUE_ANALITICO.NUMSEQUENCIAKIT IS NULL OR ESTOQUE_ANALITICO.NUMSEQUENCIAKIT <= 0)
                  AND NOTAS_ENTRADA_SAIDA.TIPOMOVIMENTO IN ('V', 'E')
                  AND ESTOQUE_ANALITICO.IDOPERACAO <> 1301
                  AND ESTOQUE_ANALITICO.DTMOVIMENTO >= ?
                  AND ESTOQUE_ANALITICO.DTMOVIMENTO < ?
            """
            stmt_margem = ibm_db.prepare(conn, sql_margem)
            ibm_db.execute(stmt_margem, (dt_ini_1, dt_fim_1))
            if ibm_db.fetch_row(stmt_margem):
                raw_lucro = ibm_db.result(stmt_margem, 0)
                raw_venda = ibm_db.result(stmt_margem, 1)
                if raw_lucro is not None and raw_venda not in (None, 0):
                    total_lucro = parse_db_number(raw_lucro)
                    total_venda_lucro = parse_db_number(raw_venda)
                    margem_calculada = True
        except Exception as margem_exc:
            logger.warning("Não foi possível calcular margem de lucro direta: %s", margem_exc)

        ibm_db.close(conn)
    except Exception as exc:
        try:
            db2_message = ibm_db.conn_errormsg(conn)
        except Exception:
            db2_message = ""
        message = f"Falha ao executar SQL: {exc}. DB2: {db2_message}".strip()
        logger.exception(message)
        try:
            ibm_db.close(conn)
        except Exception:
            pass
        REFRESH_IN_PROGRESS = False
        if cache:
            cache["status"] = "cache"
            cache["message"] = message
            return jsonify(cache)
        return jsonify(build_error_payload(message))

    try:
        vendas_por_hora = [0.0 for _ in range(24)]
        total_vendido = 0.0
        total_ontem = 0.0
        transacoes = 0
        maior_valor = 0.0
        horario_pico = "00:00"

        for linha in linhas_vendas:
            hora = int(linha.get("HORA_VENDA") or 0)
            valor = parse_db_number(linha.get("TOTAL_VENDA"))
            if linha.get("PERIODO") == "A":
                vendas_por_hora[hora] += valor
                total_vendido += valor
                transacoes += int(linha.get("QTD_CLIENTES") or 0)
                if vendas_por_hora[hora] > maior_valor:
                    maior_valor = vendas_por_hora[hora]
                    horario_pico = f"{hora:02d}:00"
            else:
                total_ontem += valor

        ticket_medio = total_vendido / transacoes if transacoes else 0.0
        variacao = ((total_vendido - total_ontem) / total_ontem * 100) if total_ontem else 0.0
        texto_variacao = f"{'↑' if variacao >= 0 else '↓'} {abs(variacao):.1f}% vs. ontem"
        if margem_calculada and total_venda_lucro:
            margem = (total_lucro / total_venda_lucro) * 100
            texto_margem = f"{'↑' if margem >= 0 else '↓'} {abs(margem):.1f}%"
        else:
            texto_margem = "N/D"

        valores_empresas = {
            int(linha["IDEMPRESA"]): parse_db_number(linha["TOTAL_VENDA"])
            for linha in linhas_empresas
        }
        empresas = [
            {"id": id_empresa, "nome": nome, "valor": valores_empresas.get(id_empresa, 0.0)}
            for id_empresa, nome in EMPRESAS.items()
        ]
        empresas.sort(key=lambda empresa: empresa["valor"], reverse=True)

        valores_empresas_mes = {
            int(linha["IDEMPRESA"]): parse_db_number(linha["TOTAL_VENDA"])
            for linha in linhas_empresas_mes
        }
        empresas_mes = [
            {"id": id_empresa, "nome": nome, "valor": valores_empresas_mes.get(id_empresa, 0.0)}
            for id_empresa, nome in EMPRESAS.items()
        ]
        empresas_mes.sort(key=lambda empresa: empresa["valor"], reverse=True)

        resposta = {
            "status": "success",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "kpis": {
                "total_vendido": format_currency(total_vendido),
                "horario_pico": f"{horario_pico} ({format_currency(maior_valor)})",
                "transacoes": f"{transacoes:,}".replace(",", "."),
                "ticket_medio": format_currency(ticket_medio),
                "margem_lucro": texto_margem,
                "comparativo": texto_variacao,
                "total_vendido_mes_atual": format_currency(total_vendido_mes_atual),
                "total_vendido_mes_anterior": format_currency(total_vendido_mes_anterior),
            },
            "grafico": {
                "categorias": [f"{h:02d}h" for h in range(24)],
                "valores": vendas_por_hora,
            },
            "empresas": empresas,
            "empresas_mes": empresas_mes,
        }

        save_cache(resposta)
        return jsonify(resposta)
    finally:
        REFRESH_IN_PROGRESS = False


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
