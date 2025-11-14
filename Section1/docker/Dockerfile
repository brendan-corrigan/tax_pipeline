FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY configs /app/configs
COPY sql /app/sql

RUN pip install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["tax-pipeline""/app/individual_tax_returns.csv", "/app/artifacts", "configs/config.yaml",]
