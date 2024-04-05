# grep'd from: https://documentation.viessmann.com/static/iot/data-points

HEATING_CIRCUIT_OPERATING_PROGRAMS = [
    "active",
    "comfort",
    "comfortCooling",
    "comfortCoolingEnergySaving",
    "comfortEnergySaving",
    "comfortHeating",
    "dhwPrecedence",
    "eco",
    "external",
    "fixed",
    "forcedLastFromSchedule",
    "frostprotection",
    "holiday",
    "holidayAtHome",
    "manual",
    "normal",
    "normalCooling",
    "normalCoolingEnergySaving",
    "normalEnergySaving",
    "normalHeating",
    "reduced",
    "reducedCooling",
    "reducedCoolingEnergySaving",
    "reducedEnergySaving",
    "reducedHeating",
    "standby",
    "summerEco",
]

HEATING_CIRCUIT_OPERATING_MODES = [
    "active",
    "cooling",
    "dhw",
    "dhwAndHeating",
    "dhwAndHeatingCooling",
    "forcedNormal",
    "forcedReduced",
    "heating",
    "heatingCooling",
    "normalStandby",
    "standby",
]

HEATING_DHW_OPERATING_MODES = ["active", "balanced", "comfort", "eco", "off"]

_ENUMS = {
    "heating_dhw_operating_modes_active_value": (
        "Active DHW operating mode",
        HEATING_DHW_OPERATING_MODES,
    ),
    "heating_circuits_operating_programs_active_value": (
        "Active heating program",
        HEATING_CIRCUIT_OPERATING_PROGRAMS,
    ),
    "heating_circuits_operating_modes_active_value": (
        "Active heating modes",
        HEATING_CIRCUIT_OPERATING_MODES,
    ),
}
