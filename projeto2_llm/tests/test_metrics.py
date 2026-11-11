from metrics import per_class, accuracy, consistency

def test_per_class_valores_conhecidos():
    y = ["a", "a", "b", "b"]; p = ["a", "b", "b", "b"]
    m = per_class(y, p, ["a", "b"])
    assert m["a"] == {"precision": 1.0, "recall": 0.5, "f1": 0.667, "support": 2}
    assert m["b"]["precision"] == 0.667 and m["b"]["recall"] == 1.0
    assert accuracy(y, p) == 0.75

def test_invalido_conta_como_erro():
    assert accuracy(["a", "b"], ["INVALIDO", "b"]) == 0.5

def test_consistencia():
    c = consistency([{1: "a", 2: "a", 3: "b"}, {1: "a", 2: "b", 3: "b"}, {1: "a", 2: "a", 3: "b"}])
    assert c["instaveis"] == 1 and c["ids_instaveis"] == [2] and c["pct_estavel"] == 66.7
