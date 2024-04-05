import pytest

from vicare_exporter.metrics import _extract_component_id


@pytest.mark.parametrize(
    ["feature", "label", "component_id", "name"],
    [
        (
            "heating_circuits_0_operating_programs_active",
            "circuits_id",
            "0",
            "heating_circuits_operating_programs_active",
        ),
        (
            "heating_burners_0_modulation",
            "burners_id",
            "0",
            "heating_burners_modulation",
        ),
        (
            "heating_burners_10_modulation",
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
