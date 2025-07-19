import datetime
import json
import os
import secrets
from pathlib import Path

from PyViCare.PyViCare import PyViCare

TEST_GATEWAY_ID = "123456789"
TEST_TIMESTAMP = "2024-04-01T01:02:03.456Z"


def anonymize(data):
    for feature in data:
        feature["gatewayId"] = TEST_GATEWAY_ID
        feature["uri"] = "<unused>"
        feature["timestamp"] = TEST_TIMESTAMP
        feature["commands"] = {}
        if feature["feature"].endswith("serial"):
            feature["properties"] = {}


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    vicare = PyViCare()

    username = os.environ["VICARE_USERNAME"]
    client_id = os.environ["VICARE_CLIENT_ID"]
    password = os.environ["VICARE_PASSWORD"]
    vicare.initWithCredentials(
        username=username,
        password=password,
        client_id=client_id,
        token_file=".vicare_token",
    )

    test_data_folder = Path(__file__).parent / "data"
    test_data_folder.mkdir(parents=True, exist_ok=True)

    prefix = secrets.token_urlsafe(4)
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    for i, device in enumerate(vicare.devices, start=1):
        device_json = device.service.fetch_all_features()
        anonymize(device_json["data"])

        with open(test_data_folder / f"{prefix}_device_{i}.json", "w") as fp:
            json.dump(device_json, fp, indent=True)
