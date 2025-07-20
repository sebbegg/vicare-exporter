ViCare Prometheus Exporter
--------------------------

vicare-exporter is small library / tool to export the features of your viessmann appliances as prometheus metrics.
You're free to use this as you like, e.g. in you own Grafana instance.

Setup and configuration
-----------------------
The project largely relies on https://github.com/openviess/PyViCare for the communication with the Viessmann API.
Check it's docs for more information.
To run the exporter, you'll at minimum need credentials for the API configured e.g. in a `.env` file:

```
VICARE_USERNAME=<your-email/username>
VICARE_PASSWORD=<password>
VICARE_CLIENT_ID=<client id>

# optional - defaults to 9100
VICARE_METRICS_PORT=9111

# optional - defaults to 120 (seconds)
# choose a larger value if you run into rate limit issues
VICARE_POLL_INTERVAL=120

# by default the gateway is ignored - to avoid rate limit issues
VICARE_IGNORE_DEVICE_IDS=gateway

# get more/less logs (default: INFO)
VICARE_LOGLEVEL=INFO

```
