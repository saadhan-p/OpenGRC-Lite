import os
import json
import time
import hmac
import hashlib
import requests
from agent.config import HOSTNAME, POLL_INTERVAL_SECONDS
from agent.plugins.firewall import FirewallPlugin
from agent.plugins.encryption import DiskEncryptionPlugin
from agent.plugins.ssh import SSHHardeningPlugin
from agent.plugins.edr import EDRCheckPlugin

CONFIG_FILE = "agent_credentials.json"
ENROLL_URL = "http://127.0.0.1:5000/api/v1/agent/enroll"
REPORT_URL = "http://127.0.0.1:5000/api/v1/agent/report"

PLUGINS = [
    FirewallPlugin(),
    DiskEncryptionPlugin(),
    SSHHardeningPlugin(),
    EDRCheckPlugin()
]


def load_or_enroll_credentials():
    """Loads stored API Key from local file or prompts for enrollment token."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get("api_key")

    print(f"[*] Agent 2.0 not enrolled. Initializing handshake with {ENROLL_URL}...")
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
    print(f"[*] Agent 2.0 Modular Collector active on host '{HOSTNAME}' ({len(PLUGINS)} plugins loaded)...")

    while True:
        batch_telemetry = []

        # Run each system plugin
        for plugin in PLUGINS:
            try:
                res = plugin.run()
                batch_telemetry.append({
                    "hostname": HOSTNAME,
                    "control_id": res["check_id"],
                    "status": res["status"],
                    "details": res["details"],
                    "evidence_hash": res["evidence_hash"],
                    "raw_evidence": res.get("raw_evidence")
                })
                print(f"  [>] {res['check_id']} -> {res['status']}: {res['details']}")
            except Exception as e:
                print(f"  [!] Plugin {plugin.check_id} failed execution: {e}")

        # Package batch payload and sign with HMAC-SHA256
        payload_bytes = json.dumps(batch_telemetry).encode('utf-8')
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
            print(f"[+] Transmitted {len(batch_telemetry)} telemetry check(s) | Status {res.status_code}: {res.text}")
        except Exception as e:
            print(f"[-] Network error transmitting telemetry: {e}")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_agent()
