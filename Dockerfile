FROM python:3.12-alpine as build

ENV PATH="/root/.local/bin:${PATH}"

COPY poetry.lock .
COPY pyproject.toml .

ADD https://install.python-poetry.org get-poetry.py

RUN python get-poetry.py --yes && \
    poetry export -o /tmp/requirements.txt

FROM python:3.12-alpine

ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

COPY --from=build /tmp/requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY vicare_exporter ./vicare_exporter

CMD [ "python", "-m", "vicare_exporter" ]
