"""Métricas por classe e consistência entre execuções (sem depender de banco)."""
from collections import Counter
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

def per_class(y_true, y_pred, labels):
    p, r, f, s = precision_recall_fscore_support(y_true, y_pred, labels=list(labels), zero_division=0)
    return {l: {"precision": round(float(p[i]), 3), "recall": round(float(r[i]), 3),
                "f1": round(float(f[i]), 3), "support": int(s[i])} for i, l in enumerate(labels)}

def accuracy(y_true, y_pred) -> float:
    return round(float(accuracy_score(y_true, y_pred)), 3)

def consistency(runs: list[dict]) -> dict:
    """runs = [{item_id: label, ...}, ...]. Fração de itens em que TODAS as execuções
    concordam, e quantos itens mudaram de rótulo entre execuções."""
    ids = set.intersection(*[set(r) for r in runs]) if runs else set()
    instaveis = [i for i in ids if len({r[i] for r in runs}) > 1]
    return {"itens": len(ids), "instaveis": len(instaveis),
            "pct_estavel": round(100 * (1 - len(instaveis) / len(ids)), 1) if ids else None,
            "ids_instaveis": sorted(instaveis)}
