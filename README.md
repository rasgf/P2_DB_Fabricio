# Gerenciador de Pedidos - P2 Banco de Dados

Esse projeto é a entrega da P2 de Banco de Dados. A ideia é simular o backend de um e-commerce moderno gerenciando pedidos.

## Tecnologias Usadas
* **FastAPI**: Pra subir a API rápida.
* **MongoDB**: Banco NoSQL pra salvar os pedidos.
* **RabbitMQ & Kafka**: Sistemas de fila pra avisar outros serviços de forma assíncrona que o pedido foi criado (Zookeeper tá subindo junto pro Kafka funcionar).
* **Pytest**: Pra garantir que a API tá rodando certo.
* **Docker**: Usando docker-compose pra subir tudo num comando só.

## Requisitos Entregues
1. ✅ Banco de dados NoSQL (Mongo) integrado.
2. ✅ ID único gerado pro pedido.
3. ✅ Status inicial do pedido como PENDENTE.
4. ✅ Mensagem publicada numa fila do RabbitMQ.
5. ✅ Evento publicado no tópico do Kafka.
6. ✅ Testes cobrindo listagem e criação de pedidos.
7. ✅ Tudo rodando em Docker (FastAPI, MongoDB, RabbitMQ, Kafka e Zookeeper).

---

## Como Rodar

Basta ter o Docker instalado e rodar o comando abaixo na pasta do projeto:

```bash
docker-compose up --build
```

Ele vai baixar as imagens e subir 5 containers:
- `mongodb` (porta 27017)
- `rabbitmq` (portas 5672 e 15672 pra tela de gerenciar)
- `zookeeper` (porta 2181)
- `kafka` (porta 9092)
- `api` (porta 8000)

Assim que o uvicorn acusar que tá rodando, você pode acessar a documentação interativa da API pelo navegador:
👉 [http://localhost:8000/docs](http://localhost:8000/docs)

## Como rodar os testes
Se você quiser rodar os testes de integração (não precisa subir o docker pra testar):
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
```
Ele vai mockar a comunicação com as filas e focar em testar a regra da API.

---

### Rotas Disponíveis (Endpoints)

* `POST /pedidos`
Recebe um JSON com `nome_cliente`, `nome_produto` e `quantidade`.
Gera o identificador, salva no Mongo com status PENDENTE e avisa o Rabbit e Kafka.

* `GET /pedidos`
Lista todos os pedidos salvos no banco NoSQL.
