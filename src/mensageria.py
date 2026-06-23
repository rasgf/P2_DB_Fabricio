import os
import json
import aio_pika
from aiokafka import AIOKafkaProducer

RABBIT_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
KAFKA_URL = os.getenv("KAFKA_URL", "localhost:9092")

# variaveis globais pro kafka e rabbit
rabbit_connection = None
rabbit_channel = None
kafka_producer = None

async def conectar_mensageria():
    global rabbit_connection, rabbit_channel, kafka_producer
    try:
        # rabbit
        rabbit_connection = await aio_pika.connect_robust(RABBIT_URL)
        rabbit_channel = await rabbit_connection.channel()
        await rabbit_channel.declare_queue("pedidos_criados", durable=True)
        print("RabbitMQ conectado!")

        # kafka
        kafka_producer = AIOKafkaProducer(bootstrap_servers=KAFKA_URL)
        await kafka_producer.start()
        print("Kafka Producer iniciado!")
    except Exception as e:
        print("Aviso: Falha ao conectar na mensageria:", e)

async def fechar_mensageria():
    global rabbit_connection, kafka_producer
    if rabbit_connection:
        await rabbit_connection.close()
    if kafka_producer:
        await kafka_producer.stop()

async def avisar_rabbit(id_pedido: str):
    if rabbit_channel:
        msg = aio_pika.Message(body=f"Pedido {id_pedido} criado com sucesso".encode())
        await rabbit_channel.default_exchange.publish(
            msg, routing_key="pedidos_criados"
        )
        print("Enviado pro Rabbit!")

async def avisar_kafka(id_pedido: str, nome_cliente: str):
    if kafka_producer:
        evento = {"evento": "PEDIDO_CRIADO", "id": id_pedido, "cliente": nome_cliente}
        await kafka_producer.send_and_wait("topico_pedidos", json.dumps(evento).encode("utf-8"))
        print("Enviado pro Kafka!")
