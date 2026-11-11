"""Classifica avaliações novas com o mesmo prompt e a mesma validação do avaliador.

  python classificar.py "Chegou rápido e funciona bem"       # um texto
  python classificar.py                                      # modo interativo
  python classificar.py --csv minhas.csv --coluna texto      # um CSV inteiro

Usa o provedor escolhido por LLM_PROVIDER (ver README) e o modelo de --model ou LLM_MODEL.
Não grava nada no Postgres: o resultado vai para o terminal ou para um CSV.
"""
import argparse, logging, os, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from compat_client import make_client
from llm import classify, DEFAULT_MODEL
from prompts import PROMPTS


def classificar_um(client, texto, system, model):
    if not isinstance(texto, str) or not texto.strip():
        return {"sentimento": None, "tema": None, "valido": False, "tentativas": 0,
                "erro": "texto vazio", "bruto": ""}
    r = classify(client, texto, system, model)
    p = r.prediction
    return {"sentimento": p.sentimento if p else None, "tema": p.tema if p else None,
            "valido": r.valid, "tentativas": r.attempts, "erro": r.error, "bruto": r.raw}


def mostrar(res):
    if res["valido"]:
        print(f"  sentimento: {res['sentimento']}")
        print(f"  tema:       {res['tema']}")
        print(f"  (tentativas: {res['tentativas']})")
    else:
        print(f"  sem resposta válida: {res['erro']}")
        if res["bruto"]:
            print(f"  resposta bruta: {res['bruto'][:200]!r}")


def modo_interativo(client, system, model):
    print(f"Modo interativo ({model}). Cole uma avaliação e aperte Enter; linha vazia para sair.")
    while True:
        try:
            texto = input("\navaliação> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not texto:
            break
        mostrar(classificar_um(client, texto, system, model))


def modo_csv(a, client, system):
    df = pd.read_csv(a.csv, sep=a.sep, engine="python", encoding="utf-8-sig", nrows=a.limite)
    if a.coluna not in df.columns:
        sys.exit(f"A coluna '{a.coluna}' não existe. Colunas do arquivo: {list(df.columns)}")
    df = df.reset_index(drop=True)
    n = len(df)
    print(f"Classificando {n} textos com {a.model} (prompt {a.prompt})...")
    resultados = []
    with ThreadPoolExecutor(a.workers) as ex:
        for i, r in enumerate(ex.map(lambda t: classificar_um(client, t, system, a.model), df[a.coluna]), 1):
            resultados.append(r)
            if i % 10 == 0 or i == n:
                print(f"  {i}/{n}")
    extra = pd.DataFrame(resultados).drop(columns=["bruto"])
    out = pd.concat([df, extra], axis=1)
    saida = a.saida or str(Path(a.csv).with_name(Path(a.csv).stem + "_classificado.csv"))
    out.to_csv(saida, index=False, encoding="utf-8-sig")
    validos = int(out["valido"].sum())
    print(f"{validos}/{n} respostas válidas -> {saida}")
    if validos:
        print(out.loc[out["valido"], "sentimento"].value_counts().to_string())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("texto", nargs="?", help="uma avaliação entre aspas")
    ap.add_argument("--csv", help="arquivo CSV com as avaliações")
    ap.add_argument("--coluna", default="texto", help="coluna com o texto no CSV (padrão: texto)")
    ap.add_argument("--sep", default=None, help="separador do CSV (padrão: detecta , ou ;)")
    ap.add_argument("--saida", help="CSV de saída (padrão: <entrada>_classificado.csv)")
    ap.add_argument("--limite", type=int, help="classifica só as N primeiras linhas")
    ap.add_argument("--prompt", default="v1", choices=PROMPTS)
    ap.add_argument("--model", default=os.getenv("LLM_MODEL", DEFAULT_MODEL))
    ap.add_argument("--workers", type=int, default=1,
                    help="chamadas em paralelo (deixe 1 se usar LLM_MIN_INTERVAL)")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, filename="classificar.log",
                        format="%(asctime)s %(levelname)s %(message)s")
    client = make_client()
    system = PROMPTS[a.prompt]
    if a.csv:
        modo_csv(a, client, system)
    elif a.texto:
        mostrar(classificar_um(client, a.texto, system, a.model))
    else:
        modo_interativo(client, system, a.model)


if __name__ == "__main__":
    main()
    