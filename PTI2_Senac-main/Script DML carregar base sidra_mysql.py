import os
import requests
import mysql.connector

# Função para conectar ao MySQL
def conectar_mysql():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "127.0.0.1"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "G@mes8090"),
            database=os.getenv("MYSQL_DATABASE", "sidra")
        )
        print("✅ Conectado ao MySQL com sucesso.")
        return conn
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao MySQL: {err}")
        exit(1)

# Inicia conexão
conn = conectar_mysql()
cursor = conn.cursor()

# Lista de consultas SIDRA e tabelas MySQL correspondentes
consultas = [
    {
        "url": "https://apisidra.ibge.gov.br/values/t/8880/v/7169/C11046/56733,56734/n3/all/p/all?formato=json",
        "tabela": "pmc_8880",
        "sql": """
            INSERT IGNORE INTO pmc_8880 (
                valor, indice, uf, mesano_codigo, mesano
            ) VALUES (%s, %s, %s, %s, %s)
        """,
        "extrair": lambda r: (
            float(r["V"]) if r.get("V", "").strip().replace('.', '', 1).isdigit() else None,
            r.get("D2N"), r.get("D3N"), r.get("D4C"), r.get("D4N")
        )
    },
    {
        "url": "https://apisidra.ibge.gov.br/values/t/8881/v/7169/C11046/56735/n3/all/p/all?formato=json",
        "tabela": "pmc_8881",
        "sql": """
            INSERT IGNORE INTO pmc_8881 (
                valor, indice, uf, mesano_codigo, mesano
            ) VALUES (%s, %s, %s, %s, %s)
        """,
        "extrair": lambda r: (
            float(r["V"]) if r.get("V", "").strip().replace('.', '', 1).isdigit() else None,
            r.get("D2N"), r.get("D3N"), int(r.get("D4C", "")), r.get("D4N")
        )
    },
    {
        "url": "https://apisidra.ibge.gov.br/values/t/8882/v/7169/C11046/56733/c85/all/n3/all/p/all?formato=json",
        "tabela": "pmc_8882",
        "sql": """
            INSERT IGNORE INTO pmc_8882 (
                valor, indice, atividades, uf, mesano_codigo, mesano
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """,
        "extrair": lambda r: (
            float(r["V"]) if r.get("V", "").strip().replace('.', '', 1).isdigit() else None,
            r.get("D2N"), r.get("D3N"), r.get("D4N"),
            r.get("D5C"), r.get("D5N")
        )
    },
    {
        "url": "https://apisidra.ibge.gov.br/values/t/8883/v/7169/C11046/56735/c85/all/n1/all/p/all?formato=json",
        "tabela": "pmc_8883",
        "sql": """
            INSERT IGNORE INTO pmc_8883 (
                valor, indice, atividades, uf, mesano_codigo, mesano
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """,
        "extrair": lambda r: (
            float(r["V"]) if r.get("V", "").strip().replace('.', '', 1).isdigit() else None,
            r.get("D2N"), r.get("D3N"), r.get("D4N"),
            r.get("D5C"), r.get("D5N")
        )
    }
]

# Processa todas as consultas
for consulta in consultas:
    print(f"\n📦 Consultando {consulta['tabela']}...")
    try:
        resp = requests.get(consulta["url"])
        data = resp.json()

        inseridos, nulos = 0, 0
        for record in data[1:]:
            try:
                valores = consulta["extrair"](record)
                if valores[0] is None:
                    nulos += 1
                cursor.execute(consulta["sql"], valores)
                inseridos += cursor.rowcount
            except Exception as e:
                print(f"⚠️ Erro ao processar registro: {e}")
                continue

        print(f"✅ {consulta['tabela']}: {inseridos} inseridos, {nulos} valores NULL.")
    except Exception as e:
        print(f"❌ Erro ao consultar {consulta['url']}: {e}")

# Finaliza conexão
conn.commit()
cursor.close()
conn.close()
print("\n🔌 Conexão finalizada.")
