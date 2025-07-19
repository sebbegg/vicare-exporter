FROM python:3.13-alpine

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PATH="/root/.local/bin:${PATH}"

COPY requirements.txt .
COPY pyproject.toml .
RUN pip install -r requirements.txt

COPY vicare_exporter ./vicare_exporter

CMD [ "python", "-m", "vicare_exporter" ]
