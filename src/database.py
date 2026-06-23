import os
from motor.motor_asyncio import AsyncIOMotorClient

# Pegando a URL do banco pelas variáveis de ambiente, ou usa localhost se não tiver
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = None
db = None

async def conectar_mongo():
    global client, db
    try:
        # conectando no mongo
        client = AsyncIOMotorClient(MONGO_URL)
        db = client.loja_pedidos # nome do banco
        print("MongoDB conectado com sucesso!")
    except Exception as e:
        print("Erro ao conectar no banco:", e)

async def fechar_mongo():
    global client
    if client:
        client.close()

def get_colecao_pedidos():
    return db["pedidos"]
