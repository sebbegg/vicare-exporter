import logging
import os
import sys

import dotenv
from prometheus_client import start_http_server
from PyViCare.PyViCare import PyViCare

from vicare_exporter.metrics import ViCareExporter

log = logging.getLogger("vicare_exporter")


if __name__ == "__main__":
    dotenv.load_dotenv()

    logging.basicConfig(
        format="%(asctime)s :: %(name)s :: %(message)s", level="INFO", stream=sys.stdout
    )

    username = os.environ["VICARE_USERNAME"]
    client_id = os.environ["VICARE_CLIENT_ID"]
    metrics_port = int(os.getenv("VICARE_METRICS_PORT", "9100"))
    interval = int(os.getenv("VICARE_POLL_INTERVAL", "120"))
    log_level = os.getenv("VICARE_LOGLEVEL", "INFO")
    ignore_devices = os.getenv("VICARE_IGNORE_DEVICE_IDS", "gateway").split(",")

    log.setLevel(log_level)

    vicare = PyViCare()
    vicare.setCacheDuration(0)
    vicare.initWithCredentials(
        username=username,
        password=os.environ["VICARE_PASSWORD"],
        client_id=client_id,
        token_file=".vicare_token",
    )

    exporter = ViCareExporter(vicare, ignore_devices)
    log.info(f"Start serving metrics on port {metrics_port}")
    log.info(f"Polling vicare features for user {username} every {interval} seconds")
    log.info(f"Using client id {client_id[:8]}***")
    if ignore_devices:
        log.info(f"Ignoring device ids: {ignore_devices}")
    start_http_server(port=metrics_port)
    exporter.poll_forever(sleep=interval)
