import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import sys
import os

# Adiciona o diretório src no path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import src.database
import src.mensageria

# Mockando a conexao com os servicos
patch('src.database.AsyncIOMotorClient', new_callable=AsyncMock).start()
patch('src.mensageria.aio_pika.connect_robust', new_callable=AsyncMock).start()
patch('src.mensageria.AIOKafkaProducer', new_callable=AsyncMock).start()

from src.main import app
from src.database import get_colecao_pedidos

client = TestClient(app)

def test_cadastro_pedido():
    # Fingindo que o MongoDB inseriu certinho e ignorando envio nas filas
    with patch('src.main.get_colecao_pedidos') as mock_mongo, \
         patch('src.main.avisar_rabbit', new_callable=AsyncMock) as mock_rabbit, \
         patch('src.main.avisar_kafka', new_callable=AsyncMock) as mock_kafka:
         
        mock_colecao = AsyncMock()
        mock_mongo.return_value = mock_colecao
        
        payload = {
            "nome_cliente": "Joao Teste",
            "nome_produto": "Notebook Gamer",
            "quantidade": 1
        }
        
        response = client.post("/pedidos", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["nome_cliente"] == "Joao Teste"
        assert data["status_pedido"] == "PENDENTE"
        assert "identificador_unico" in data
        
        # garante que as paradas foram chamadas
        mock_colecao.insert_one.assert_called_once()
        mock_rabbit.assert_called_once()
        mock_kafka.assert_called_once()

def test_listar_pedidos():
    with patch('src.main.get_colecao_pedidos') as mock_mongo:
        # Mockando a iteracao async no motor
        class AsyncIterator:
            def __init__(self, items):
                self.items = items
            def __aiter__(self):
                self.it = iter(self.items)
                return self
            async def __anext__(self):
                try:
                    return next(self.it)
                except StopIteration:
                    raise StopAsyncIteration

        from unittest.mock import MagicMock
        mock_colecao = AsyncMock()
        mock_colecao.find = MagicMock(return_value=AsyncIterator([
            {
                "identificador_unico": "123",
                "nome_cliente": "Maria",
                "nome_produto": "Mouse",
                "quantidade": 2,
                "status_pedido": "PENDENTE"
            }
        ]))
        mock_mongo.return_value = mock_colecao
        
        response = client.get("/pedidos")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["nome_cliente"] == "Maria"
