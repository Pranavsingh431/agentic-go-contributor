FROM golang:1.21 AS go_base

FROM python:3.11-slim

COPY --from=go_base /usr/local/go /usr/local/go
ENV PATH="/usr/local/go/bin:${PATH}"

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
