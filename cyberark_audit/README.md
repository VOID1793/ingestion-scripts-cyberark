# CyberArk Audit

This script fetches batched logs from CyberArk Audit and sends them to Google SecOps

## CyberArk ENV Variables

| Variable | Description | Required | Default | Secret |
| --- | --- | --- | --- | --- |
| CYBERARK_OAUTH_CLIENT_ID | OAuth Confidential Username for SIEM-Integration | Yes | - | Yes |
| CYBERARK_OAUTH_CLIENT_SECRET | OAuth Confidential Secret for SIEM-Integration | Yes | - | Yes |
| CYBERARK_AUDIT_API_KEY | CyberArk Audit "Third Party SIEM Integration" API Key | Yes | - | Yes
| CYBERARK_IDENTITY_SIEM_APP_ID | CyberArk Identity WebApp Oauth2 AppID for your "Third Party SIEM Integration" | Yes | - | Yes
| CYBERARK_IDENTITY_SUBDOMAIN | CyberArk Identity Tenant ID | Yes | - | Yes
| CYBERARK_ISPSS_SUBDOMAIN | CyberArk shared services subdomain | Yes | - | Yes
| GCP_BUCKET_NAME | GCP Storage Bucket name for where to deposit the time state file | Yes | - | Yes

## Relevant Documentation

* [Identity WebApp Creation](https://docs.cyberark.com/admin-space/latest/en/content/siem-integration/siem-export-3rd-party.htm)
* [SIEM Integration API](https://docs.cyberark.com/audit/latest/en/content/audit/isp_siem-integration-api.htm)

## Test CURL Templates

```shell
curl --request POST \
  --url https://<identity_id>.id.cyberark.cloud/OAuth2/Token/<oauth2_app> \
  --header 'authorization: Basic <b64 encoded user:pass>' \
  --header 'content-type: application/x-www-form-urlencoded' \
  --data grant_type=client_credentials \
  --data scope=isp.audit.events:read

curl --request POST \
  --url https://<tenant>-<region>.audit.cyberark.cloud/api/audits/stream/createQuery \
  --header 'authorization: Bearer <access_token>' \
  --header 'content-type: application/json' \
  --header 'x-api-key: <api-key>' \
  --data '{
  "filterModel": {
    "date": {
      "dateFrom": "2026-02-25T00:00:00.000Z"
    }
  }
}'

curl --request POST \
  --url https://<tenant>-<region>.audit.cyberark.cloud/api/audits/stream/results \
  --header 'authorization: Bearer <access_token>' \
  --header 'content-type: application/json' \
  --header 'x-api-key: <api-key>' \
  --data '{
  "cursorRef": "<cursor_ref>"
}'
```

## Plan

* Access google storage container

* Time assignment:
    * FROM = TO (read from the blob)
    * TO   = CURRENT TIME

* Auth/Authn to the CyberArk Identity API Endpoint (CyberArk SDK)

* Build the query body in JSON
    * Identity Logs
    * Conjur Logs
    * Privilege Cloud Logs

* Retrieve a cursorRef from the Audit API (requests)

* Retrieve the payload via the cursorRef (requests)

* Run the ingestion function to send payload to Chronicle

* Validate successful payload reception into Chronicle (HTTP 200)

* Update the blob with the FROM and TO that was set at the beginning of the run (only if successful)

* De-Auth



IMPORTS:

* from google.cloud
    * import storage
* from common
    * from common import env_constants
    * from common import ingest
    * from common import utils
* import datetime
* import json
* import time
