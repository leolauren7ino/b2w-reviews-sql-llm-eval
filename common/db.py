"""Conexão única com o Postgres, configurável por variáveis de ambiente."""
import os
import psycopg2

def connect():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "/tmp"),
        port=int(os.getenv("PGPORT", "5433")),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
        dbname=os.getenv("PGDATABASE", "portfolio"),
    )
