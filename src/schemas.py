from pydantic import BaseModel
from typing import Optional

class PedidoCreate(BaseModel):
    nome_cliente: str
    nome_produto: str
    quantidade: int

class PedidoResponse(BaseModel):
    identificador_unico: str
    nome_cliente: str
    nome_produto: str
    quantidade: int
    status_pedido: str
