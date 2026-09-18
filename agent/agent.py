import os
import json
import time
import hmac
import hashlib
import requests
from agent.config import HOSTNAME, POLL_INTERVAL_SECONDS
from agent.plugins.firewall import check_firewall

CONFIG_FILE = "agent_credentials.json"
ENROLL_URL = "http://127.0.0.1:5000/api/v1/agent/enroll"
REPORT_URL = "http://127.0.0.1:5000/api/v1/agent/report"


def load_or_enroll_credentials():
    """Loads stored API Key from local file or prompts for enrollment token."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get("api_key")

    print(f"[*] Agent not enrolled. Initializing handshake with {ENROLL_URL}...")
    enrollment_token = input("Enter Enrollment Token: ").strip()

    payload = {
        "enrollment_token": enrollment_token,
        "hostname": HOSTNAME,
        "os_type": "Linux"
    }

    resp = requests.post(ENROLL_URL, json=payload)
    if resp.status_code == 201:
        res_data = resp.json()
        api_key = res_data["agent_api_key"]
        with open(CONFIG_FILE, "w") as f:
            json.dump({"hostname": HOSTNAME, "api_key": api_key}, f)
        print(f"[+] Enrollment successful! API Key stored in {CONFIG_FILE}")
        return api_key
    else:
        print(f"[-] Enrollment failed ({resp.status_code}): {resp.text}")
        exit(1)


def compute_hmac_signature(payload_bytes: bytes, timestamp_str: str, api_key: str) -> str:
    message = payload_bytes + timestamp_str.encode('utf-8')
    return hmac.new(api_key.encode('utf-8'), message, hashlib.sha256).hexdigest()


def run_agent():
    api_key = load_or_enroll_credentials()
    print(f"[*] Authenticated Agent running on {HOSTNAME}...")

    while True:
        fw_status, fw_msg = check_firewall()
        payload = {
            "hostname": HOSTNAME,
            "control_id": "A.13.1 (Network)",
            "status": fw_status,
            "details": fw_msg
        }

        payload_bytes = json.dumps(payload).encode('utf-8')
        timestamp_str = str(time.time())
        signature = compute_hmac_signature(payload_bytes, timestamp_str, api_key)

        headers = {
            "Content-Type": "application/json",
            "X-Agent-ID": HOSTNAME,
            "X-Timestamp": timestamp_str,
            "X-Signature": signature
        }

        try:
            res = requests.post(REPORT_URL, data=payload_bytes, headers=headers)
            print(f"[+] Report Status {res.status_code}: {res.text}")
        except Exception as e:
            print(f"[-] Request failed: {e}")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_agent()
