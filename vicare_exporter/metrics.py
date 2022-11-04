import logging
import re
import time
from datetime import datetime

from prometheus_client import Enum, Gauge
from PyViCare.PyViCare import PyViCare
from PyViCare.PyViCareUtils import PyViCareInternalServerError, PyViCareRateLimitError

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

_component_re = re.compile(r"^heating_(.*)_(\d+)(.*)")


def _extract_circuit_id(feature_name) -> tuple[str, str]:
    component_match = _component_re.match(feature_name)
    if component_match:
        component_id = component_match.group(2)
        name = _component_re.sub(r"heating_\1\3", feature_name)
        label = component_match.group(1) + "_id"
        return component_id, label, name

    else:
        return None, None, feature_name


# want this memoized so we don't create duplicated metrics
_metrics = {}


def get_metric_for_name(name: str, labels: list[str]):
    if name in _metrics:
        return _metrics[name]

    if name.endswith("_operating_modes_active_value"):
        _metrics[name] = Enum(
            name,
            "Active heatings modes",
            states=["standby", "dhw", "dhwAndHeating", "forcedReduced", "forcedNormal"],
            labelnames=labels,
        )
    elif name.endswith("_operating_programs_active_value"):
        _metrics[name] = Enum(
            name,
            "Active heating program",
            states=[
                "active",
                "comfort",
                "eco",
                "external",
                "holiday",
                "normal",
                "reduced",
                "standby",
            ],
            labelnames=labels,
        )
    elif name.endswith("_status"):
        _metrics[name] = Enum(
            name, "Status", states=["error", "connected"], labelnames=labels
        )
    else:
        _metrics[name] = Gauge(name, name, labelnames=labels)

    return _metrics[name]


def extract_feature_metrics(feature: dict, installation_id: str):

    props = feature.get("properties")
    if not props:
        return []

    feature_name = feature["feature"].replace(".", "_")

    labels = dict(
        gateway_id=feature["gatewayId"],
        device_id=feature["deviceId"],
        installation_id=installation_id,
    )

    # check if this is a heating circuit metric
    component_id, label_name, feature_name = _extract_circuit_id(feature_name)
    if component_id is not None:
        labels[label_name] = component_id

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
        if prop == "status" and value in ("on", "off"):
            prop = "on"
            value = value == "on"

        if unit:
            name = "_".join((feature_name, prop, unit))
        else:
            name = "_".join((feature_name, prop))

        metric = get_metric_for_name(name, sorted(labels))
        if isinstance(metric, Gauge):
            metric.labels(**labels).set(value)
        else:
            metric.labels(**labels).state(value)


def _fetch_devices_features(vicare: PyViCare) -> int:

    n_features = 0
    for device in vicare.devices:
        features = device.service.fetch_all_features()

        for feature in features["data"]:
            extract_feature_metrics(feature, installation_id=device.service.accessor.id)
            n_features += 1

    return n_features


def poll(vicare: PyViCare):
    t = time.time()

    try:
        n_features = _fetch_devices_features(vicare)
    except PyViCareInternalServerError:
        log.error(
            "An ViCare internal error occured",
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
