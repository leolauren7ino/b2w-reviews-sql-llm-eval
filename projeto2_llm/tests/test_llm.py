from types import SimpleNamespace as NS
from llm import classify, extract_json

def resp(text, stop="end_turn"):
    return NS(content=[NS(type="text", text=text)], stop_reason=stop)

class Stub:
    def __init__(self, *outs):
        self.outs, self.calls = list(outs), []
        self.messages = self
    def create(self, **kw):
        self.calls.append(kw)
        o = self.outs.pop(0)
        if isinstance(o, Exception):
            raise o
        return o

OK = '{"sentimento": "positivo", "tema": "entrega"}'
nosleep = lambda s: None

def test_json_puro():
    r = classify(Stub(resp(OK)), "x", "sys", sleep=nosleep)
    assert r.valid and r.attempts == 1 and r.prediction.tema == "entrega"

def test_json_em_cerca_de_codigo_e_prosa():
    assert extract_json(f"Claro!\n```json\n{OK}\n```") == {"sentimento": "positivo", "tema": "entrega"}
    assert extract_json(f"Resposta: {OK} espero ter ajudado")["tema"] == "entrega"

def test_json_quebrado_faz_retry_e_manda_o_erro_de_volta():
    c = Stub(resp('{"sentimento": "positivo", '), resp(OK))
    r = classify(c, "x", "sys", sleep=nosleep)
    assert r.valid and r.attempts == 2 and r.errors_seen == ["json_quebrado"]
    assert "inválida" in c.calls[1]["messages"][-1]["content"]

def test_valor_fora_da_taxonomia_e_rejeitado():
    bad = '{"sentimento": "feliz", "tema": "entrega"}'
    r = classify(Stub(resp(bad), resp(bad), resp(bad)), "x", "sys", sleep=nosleep)
    assert not r.valid and r.attempts == 3 and "fora_do_esquema" in r.error

def test_campo_extra_e_rejeitado():
    r = classify(Stub(*[resp('{"sentimento":"positivo","tema":"outro","extra":1}')] * 3), "x", "sys", sleep=nosleep)
    assert not r.valid

def test_erro_de_api_e_refusal_contam_como_tentativa():
    c = Stub(RuntimeError("boom"), resp("", stop="refusal"), resp(OK))
    r = classify(c, "x", "sys", sleep=nosleep)
    assert r.valid and r.attempts == 3 and r.errors_seen == ["api:RuntimeError", "stop:refusal"]

def test_nunca_valido_nao_levanta_excecao():
    r = classify(Stub(*[RuntimeError("x")] * 3), "x", "sys", sleep=nosleep)
    assert not r.valid and r.prediction is None
