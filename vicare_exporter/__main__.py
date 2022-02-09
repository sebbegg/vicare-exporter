from datetime import datetime
import logging
import os
import sys
import time

from prometheus_client import start_http_server
from PyViCare.PyViCare import PyViCare
from PyViCare.PyViCareUtils import PyViCareInternalServerError, PyViCareRateLimitError

from vicare_exporter.metrics import extract_feature_metrics

log = logging.getLogger("vicare_exporter")


def _fetch_devices_features(vicare: PyViCare) -> int:

    n_features = 0
    for device in vicare.devices:
        features = device.service.fetch_all_features()

        for feature in features["data"]:
            extract_feature_metrics(feature, installation_id=device.service.accessor.id)
            n_features += 1

    return n_features


def loop(vicare: PyViCare, sleep=120):

    while True:

        t = time.time()

        try:
            n_features = _fetch_devices_features(vicare)
        except PyViCareInternalServerError as err:
            log.error(f"An ViCare internal error occured - will try again in {sleep} seconds", exc_info=True)
        except PyViCareRateLimitError as err:
            log.error(err.message)
            log.error("Waiting until rate limit reset.")
            time.sleep((err.limitResetDate - datetime.now()).total_seconds())
        else:
            log.info(f"Fetched {n_features} features in {time.time() - t:g} seconds")

        try:
            time.sleep(sleep)
        except KeyboardInterrupt:
            log.info("Shutting down.")
            return


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s :: %(name)s :: %(message)s", level="INFO", stream=sys.stdout
    )

    vicare = PyViCare()
    vicare.initWithCredentials(
        username=os.environ["VICARE_USERNAME"],
        password=os.environ["VICARE_PASSWORD"],
        client_id=os.environ["VICARE_CLIENT_ID"],
        token_file=".vicare_token",
    )
    vicare.setCacheDuration(1)

    metrics_port = int(os.getenv("VICARE_EXPORTER_PORT", "9100"))
    log.info(f"Start serving metrics on port {metrics_port}")
    start_http_server(port=metrics_port)
    loop(vicare)
