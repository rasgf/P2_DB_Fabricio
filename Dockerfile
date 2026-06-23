FROM python:3.12-slim

WORKDIR /app

# Copia os requirements
COPY requirements.txt .

# Instala as dependencias do pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia a pasta src
COPY src/ src/

# Variaveis de ambiente padrao (serao sobrescritas pelo compose)
ENV PYTHONPATH=/app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
