import logging
import os
import signal
import sys
import threading

import dotenv
from prometheus_client import REGISTRY, start_http_server
from PyViCare.PyViCare import PyViCare

from vicare_exporter import LOGGER, ViCareCollector

def main():
    dotenv.load_dotenv()

    logging.basicConfig(
        format="%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s",
        level="INFO",
        stream=sys.stdout,
    )

    username = os.environ["VICARE_USERNAME"]
    client_id = os.environ["VICARE_CLIENT_ID"]
    metrics_port = int(os.getenv("VICARE_METRICS_PORT", "9100"))
    interval = int(os.getenv("VICARE_POLL_INTERVAL", "120"))
    log_level = os.getenv("VICARE_LOGLEVEL", "INFO")
    ignore_devices = os.getenv("VICARE_IGNORE_DEVICE_IDS", "gateway").split(",")

    LOGGER.setLevel(log_level)

    vicare = PyViCare()
    vicare.setCacheDuration(0)
    vicare.initWithCredentials(
        username=username,
        password=os.environ["VICARE_PASSWORD"],
        client_id=client_id,
        token_file=".vicare_token",
    )

    vicare_collector = ViCareCollector(
        vicare, ignore_devices, min_fetch_interval_seconds=interval
    )
    LOGGER.info(f"Start serving metrics on port {metrics_port}")
    LOGGER.info(f"Polling vicare features for user {username} every {interval} seconds")
    LOGGER.info(f"Using client id {client_id[:8]}***")
    if ignore_devices:
        LOGGER.info(f"Ignoring device ids: {ignore_devices}")

    REGISTRY.register(vicare_collector)
    start_http_server(port=metrics_port)

    stop_event = threading.Event()

    def do_stop(*_):
        LOGGER.info("Received stop signal.")
        stop_event.set()

    signal.signal(signal.SIGINT, do_stop)
    signal.signal(signal.SIGTERM, do_stop)
    stop_event.wait()

if __name__ == "__main__":
    main()
