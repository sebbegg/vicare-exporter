FROM python:3.9-alpine

COPY requirements.txt .

RUN pip install -U pip && \
    pip install -r requirements.txt


COPY vicare_exporter ./vicare_exporter

CMD [ "python", "-m", "vicare_exporter" ]