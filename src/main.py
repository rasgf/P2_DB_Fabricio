import uuid
from fastapi import FastAPI, HTTPException
from src.schemas import PedidoCreate, PedidoResponse
from src.database import conectar_mongo, fechar_mongo, get_colecao_pedidos
from src.mensageria import conectar_mensageria, fechar_mensageria, avisar_rabbit, avisar_kafka

app = FastAPI(title="Gerenciamento de Pedidos (NoSQL)")

@app.on_event("startup")
async def startup_db_client():
    # conecta em tudo quando inicia
    await conectar_mongo()
    await conectar_mensageria()

@app.on_event("shutdown")
async def shutdown_db_client():
    await fechar_mongo()
    await fechar_mensageria()

@app.post("/pedidos", response_model=PedidoResponse, status_code=201)
async def criar_pedido(pedido: PedidoCreate):
    colecao = get_colecao_pedidos()
    
    # gerando id manual para garantir que seja unico e facil de ler
    novo_id = str(uuid.uuid4().hex)
    
    # status inicial pedido pelo prof
    status_inicial = "PENDENTE"
    
    documento = {
        "identificador_unico": novo_id,
        "nome_cliente": pedido.nome_cliente,
        "nome_produto": pedido.nome_produto,
        "quantidade": pedido.quantidade,
        "status_pedido": status_inicial
    }
    
    # salva no mongo
    await colecao.insert_one(documento)
    
    # avisa os sistemas externos
    await avisar_rabbit(novo_id)
    await avisar_kafka(novo_id, pedido.nome_cliente)
    
    # nao podemos retornar o '_id' do mongo direto, entao criamos o dict de resposta
    resposta = {
        "identificador_unico": novo_id,
        "nome_cliente": pedido.nome_cliente,
        "nome_produto": pedido.nome_produto,
        "quantidade": pedido.quantidade,
        "status_pedido": status_inicial
    }
    
    return resposta

@app.get("/pedidos", response_model=list[PedidoResponse])
async def listar_pedidos():
    colecao = get_colecao_pedidos()
    pedidos = []
    
    # iterando pelo cursor do motor
    cursor = colecao.find({})
    async for documento in cursor:
        pedidos.append({
            "identificador_unico": documento["identificador_unico"],
            "nome_cliente": documento["nome_cliente"],
            "nome_produto": documento["nome_produto"],
            "quantidade": documento["quantidade"],
            "status_pedido": documento["status_pedido"]
        })
        
    return pedidos
