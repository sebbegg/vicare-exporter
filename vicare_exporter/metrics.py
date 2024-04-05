import functools
import logging
import time
from datetime import datetime
from typing import Optional

from prometheus_client import Enum, Gauge
from PyViCare.PyViCare import PyViCare
from PyViCare.PyViCareUtils import PyViCareInternalServerError, PyViCareRateLimitError

from .enums import _ENUMS

log = logging.getLogger("vicare_exporter")

UNITS = {"kilowattHour": "kWh"}
PROPERTY_NAMES = [
    "active",
    "currentDay",
    "day",
    "hours",
    "shift",
    "slope",
    "starts",
    "status",
    "temperature",
    "value",
]


def _extract_component_id(feature_name) -> tuple[Optional[str], Optional[str], str]:
    parts: list[str] = feature_name.split("_")
    prev = parts[0]
    for i, part in enumerate(parts[1:], start=1):
        if part.isdigit():
            component_id = part
            label = prev + "_id"
            name = "_".join(parts[:i] + parts[i + 1 :])
            return component_id, label, name
        prev = part

    return None, None, feature_name


@functools.cache
def get_metric_for_name(name: str, labels: tuple[str]):

    log.debug("Getting metric for: %s", name)
    documentation, states = _ENUMS.get(name, (None, None))
    if documentation:
        return Enum(
            name,
            documentation=documentation,
            states=states,
            labelnames=labels,
        )

    if name.endswith("_status"):
        return Enum(name, "Status", states=["error", "connected"], labelnames=labels)
    else:
        return Gauge(name, name, labelnames=labels)


def extract_feature_metrics(feature: dict, installation_id: str):

    props = feature.get("properties")
    if not props:
        return []

    metric_name = feature["feature"].replace(".", "_")

    labels = dict(
        gateway_id=feature["gatewayId"],
        device_id=feature["deviceId"],
        installation_id=installation_id,
    )

    # check if this is a heating circuit/burners metric
    component_id, label_name, metric_name = _extract_component_id(metric_name)
    if component_id is not None:
        labels[label_name] = component_id

    label_names = tuple(sorted(labels))
    for prop in PROPERTY_NAMES:
        if prop not in props:
            continue
        unit = props[prop].get("unit", "")
        unit = UNITS.get(unit, unit)

        value = props[prop]["value"]
        # pick only the current day as metric
        if prop == "day":
            value = value[0]

        # map on/off to true/false
        elif prop == "status" and value in ("on", "off"):
            prop = "on"
            value = value == "on"

        if unit:
            name = "_".join((metric_name, prop, unit))
        else:
            name = "_".join((metric_name, prop))

        metric = get_metric_for_name(name, label_names)
        if isinstance(metric, Gauge):
            metric.labels(**labels).set(value)
        else:
            metric.labels(**labels).state(value)


def _fetch_devices_features(vicare: PyViCare) -> int:

    n_features = 0
    for device in vicare.devices:
        features = device.service.fetch_all_features()

        for feature in features.get("data", []):
            extract_feature_metrics(feature, installation_id=device.service.accessor.id)
            n_features += 1

    return n_features


def poll(vicare: PyViCare):
    t = time.time()

    try:
        n_features = _fetch_devices_features(vicare)
    except PyViCareInternalServerError:
        log.error(
            "An ViCare internal error occurred",
            exc_info=True,
        )
    else:
        log.info(f"Fetched {n_features} features in {time.time() - t:g} seconds")


def poll_forever(vicare: PyViCare, sleep=120):

    while True:

        try:
            poll(vicare)
        except PyViCareRateLimitError as err:
            log.error(err.message)
            log.error("Waiting until rate limit reset.")
            time.sleep((err.limitResetDate - datetime.now()).total_seconds())

        try:
            time.sleep(sleep)
        except KeyboardInterrupt:
            log.info("Shutting down.")
            return
