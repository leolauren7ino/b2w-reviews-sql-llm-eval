"""Taxonomia e contrato de saída. É aqui que a 'confiança no modelo' começa:
qualquer coisa fora deste esquema é tratada como falha, não como resposta."""
from typing import Literal
from pydantic import BaseModel, ConfigDict

SENTIMENTOS = ("positivo", "neutro", "negativo")
TEMAS = ("entrega", "qualidade_produto", "preco", "atendimento", "anuncio_divergente", "outro")

class Prediction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sentimento: Literal["positivo", "neutro", "negativo"]
    tema: Literal["entrega", "qualidade_produto", "preco", "atendimento", "anuncio_divergente", "outro"]
