import glob
import json

import pytest

from vicare_exporter.metrics import _extract_component_id, extract_feature_metrics


@pytest.mark.parametrize(
    ["feature", "label", "component_id", "name"],
    [
        (
            "heating.circuits.0.operating.programs.active",
            "circuits_id",
            "0",
            "heating_circuits_operating_programs_active",
        ),
        (
            "heating.burners.0.modulation",
            "burners_id",
            "0",
            "heating_burners_modulation",
        ),
        (
            "heating.burners.10.modulation",
            "burners_id",
            "10",
            "heating_burners_modulation",
        ),
    ],
)
def test_component_id_extractor(feature: str, label: str, component_id: str, name: str):

    feature_id, feature_label, feature_name = _extract_component_id(feature)
    assert feature_id == component_id
    assert feature_label == label
    assert feature_name == name


@pytest.mark.parametrize("data_file", sorted(glob.glob("tests/data/*_device_*.json")))
def test_data(data_file: str):
    with open(data_file, "r") as fp:
        device = json.load(fp)

    for feature in device["data"]:
        extract_feature_metrics(feature, installation_id="dummy")
