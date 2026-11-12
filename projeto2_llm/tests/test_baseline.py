"""Testes do baseline sem dataset real: lógica de rótulo, vazamento e split idêntico ao split.py."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import baseline_tfidf as b  # noqa: E402

LABELING = Path(__file__).resolve().parent.parent / "labeling"


def test_stars_to_sentiment():
    assert [b.stars_to_sentiment(s) for s in (1, 2, 3, 4, 5)] == ["negativo", "negativo", "neutro", "positivo", "positivo"]


def test_gold_split_is_balanced_and_disjoint():
    s = b.load_gold_splits(LABELING)
    assert len(s["dev"]) == len(s["test"]) == 100
    assert not set(s["dev"].review_id) & set(s["test"].review_id)
    # estratificado: mesma contagem de neutros (±1) nos dois lados
    assert abs((s["dev"].sentimento == "neutro").sum() - (s["test"].sentimento == "neutro").sum()) <= 1


def test_training_excludes_gold_and_duplicates(tmp_path):
    raw = pd.DataFrame({
        "review_text": ["texto do gabarito que é bem longo aqui ok", "ótimo produto, chegou rápido e bem embalado",
                        "ótimo produto, chegou rápido e bem embalado", "péssimo, quebrou no primeiro dia de uso mesmo",
                        "curto", None],
        "overall_rating": [5, 5, 5, 1, 5, 3],
    })
    p = tmp_path / "raw.csv"
    raw.to_csv(p, index=False)
    tr = b.load_training(p, {"texto do gabarito que é bem longo aqui ok"})
    assert len(tr) == 2  # sem gabarito, sem duplicata, sem curto, sem nulo
    assert set(tr.sentimento) == {"positivo", "negativo"}


def test_pipeline_learns_and_evaluates():
    pos = ["adorei o produto, muito bom e chegou rápido"] * 30
    neg = ["horrível, veio quebrado e não recomendo"] * 30
    df = pd.DataFrame({"review_text": pos + neg, "sentimento": ["positivo"] * 30 + ["negativo"] * 30})
    m = b.build_model().set_params(tfidfvectorizer__min_df=1)
    m.fit(df.review_text, df.sentimento)
    res = b.evaluate(m, df)
    assert res["accuracy"] == 1.0
    assert res["confusion"].loc["neutro"].sum() == 0
    lo, hi = res["ci95"]
    assert lo <= res["accuracy"] <= hi


def test_bootstrap_ci_is_wide_for_100_items():
    correct = np.array([1.0] * 95 + [0.0] * 5)
    lo, hi = b.bootstrap_ci(correct)
    assert 0.88 <= lo < 0.95 < hi <= 1.0
