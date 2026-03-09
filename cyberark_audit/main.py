# Ingestion functions intended to retrieve data payloads
# from the CyberArk Audit service, split them, and then
# send them to the appropriate backend receiver for Google
# SecOps SIEM.

"""Fetch logs from the CyberArk Audit API and ingest them to SecOps."""

import json
import os # For TESTING! with outfiles!
import base64
from datetime import datetime, timezone
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

# from google.cloud import storage

# from common import ingest
# from common import utils


# CyberArk Identity Basic Auth. ID
CYBERARK_OAUTH_CLIENT_ID = (os.environ["CYBERARK_OAUTH_CLIENT_ID"])
# CyberArk Identity Basic Auth. Secret
CYBERARK_OAUTH_CLIENT_SECRET = (os.environ["CYBERARK_OAUTH_CLIENT_SECRET"])
# CyberArk Audit API Key
CYBERARK_AUDIT_API_KEY = (os.environ["CYBERARK_AUDIT_API_KEY"])
# CyberArk Identity URL for the SIEM Integration WebApp
CYBERARK_IDENTITY_SIEM_APP_ID = (os.environ["CYBERARK_IDENTITY_SIEM_APP_ID"])
#CyberArk Identity Subdomain 
CYBERARK_IDENTITY_SUBDOMAIN = (os.environ["CYBERARK_IDENTITY_SUBDOMAIN"])
# CyberArk Subdomain as it would appear in the Audit URL
CYBERARK_ISPSS_SUBDOMAIN = (os.environ["CYBERARK_ISPSS_SUBDOMAIN"])
# Google Storage Account Name
# GCP_BUCKET_NAME = (os.environ["GCP_BUCKET_NAME"])

# Function to retrieve the last range of logs from the Google Storage location
# def get_last_range() -> str:


# Function to construct and return a valid query body for the Audit API to ingest and receive
def build_query_body(start_date: str) -> str:
    print("Building the Audit query... ")

    now_utc = datetime.now(timezone.utc)
    current_date = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ") + "Z"
    print(current_date)

    query = {
        
        "filterModel": {
            "date": {
                "dateFrom": "2026-02-25T00:00:00Z", #start_date #TESTING HARD CODED DATE RANGE
                "dateTo"  : current_date
            }
        }
    }

    query_json = json.dumps(query, indent=3)

    return query_json



# Function to authenticate to the CyberArk SIEM Web Application in Identity and retrieve an Auth Token to grab a log payload from Audit
def get_log_payload(client_id: str, client_secret: str, id_subdomain: str, siem_app_id: str, audit_subdomain: str, audit_api_key: str, query: str) -> str:
    
    siem_url = f"https://{id_subdomain}.id.cyberark.cloud/OAuth2/token/{siem_app_id}" 

    audit_cursor_url = f"https://{audit_subdomain}.audit.cyberark.cloud/api/audits/stream/createQuery"
    audit_results_url = f"https://{audit_subdomain}.audit.cyberark.cloud/api/audits/stream/results"
    
    audit_headers = {
        "x-api-key": audit_api_key
    }

    
    print("Authenticating to Identity's SIEM WebApplication... ")

    id_auth = HTTPBasicAuth(client_id, client_secret)
    scope   = "isp.audit.events:read"
    client  = BackendApplicationClient(client_id=client_id, scope=scope)
    oauth2  = OAuth2Session(client=client)
    
    oauth2.fetch_token(
        token_url = siem_url,
        auth      = id_auth
    )

    try:
        print("Retrieving cursor reference... ")
        cursor_response = oauth2.post(
            url     = audit_cursor_url,
            data    = query,
            headers = audit_headers
        )

        cursorRef = cursor_response.json()
        body = {"cursorRef" : (cursorRef.get("cursorRef"))}
        print("Retrieving log payload... ")
        log_response = oauth2.post(
            url     = audit_results_url,
            json    = body,
            headers = audit_headers
        )

        logs = log_response.json()
    except:
        print("Error")



    return logs



# Function to tag and send the logs to SecOps
# def send_log(log_json: str) -> str:



# Function to update the Google BLOB with the new data/time range
# def update_range() -> None:



# Main function
def main():
    
    query = build_query_body("dummy")

    logs = get_log_payload(
        CYBERARK_OAUTH_CLIENT_ID, 
        CYBERARK_OAUTH_CLIENT_SECRET, 
        CYBERARK_IDENTITY_SUBDOMAIN, 
        CYBERARK_IDENTITY_SIEM_APP_ID, 
        CYBERARK_ISPSS_SUBDOMAIN, 
        CYBERARK_AUDIT_API_KEY, 
        query
    )
    
    with open('audit.json', 'w') as f:
        json.dump(logs, f, indent=4)

if __name__ == "__main__":
    main()
