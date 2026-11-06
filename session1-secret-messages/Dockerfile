FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY secretmsgs ./secretmsgs
# editable install keeps the package next to web/ and wordlists/
RUN pip install --no-cache-dir -e .
COPY web ./web
COPY wordlists ./wordlists
