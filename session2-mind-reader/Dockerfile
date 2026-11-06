FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY mindreader ./mindreader
# editable install keeps the package next to web/
RUN pip install --no-cache-dir -e .
COPY web ./web
# --no-access-log: quiz traffic is never written to logs
CMD ["uvicorn", "mindreader.app:app", "--host", "0.0.0.0", "--port", "8100", "--no-access-log"]
