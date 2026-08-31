FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip install --no-cache-dir -e .

COPY . .

RUN mkdir -p /app/data && chmod 777 /app/data

EXPOSE 5000

CMD ["python", "main.py"]