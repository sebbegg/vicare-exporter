FROM python:3.9-alpine


ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PATH="/root/.local/bin:${PATH}"

COPY poetry.lock .
COPY pyproject.toml .

ADD https://install.python-poetry.org get-poetry.py

RUN python get-poetry.py --yes && \
    poetry config virtualenvs.create false && \
    poetry install && \
    pip uninstall -y pip && \
    python get-poetry.py --uninstall

COPY vicare_exporter ./vicare_exporter

CMD [ "python", "-m", "vicare_exporter" ]
