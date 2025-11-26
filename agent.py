import requests
import time
import socket
import random

SERVER_URL = "http://127.0.0.1:5000/api/report"
HOSTNAME = socket.gethostname()

def check_firewall():
    # Simulating a check. In real life, use subprocess to check 'ufw' status.
    # 90% chance of pass, 10% chance of failure (to test the dashboard)
    if random.random() > 0.1:
        return "PASS", "Firewall is active and filtering traffic."
    else:
        return "FAIL", "CRITICAL: Firewall service is DOWN."

def check_password_policy():
    return "PASS", "Password complexity requirements met."

def run_agent():
    print(f"[*] Agent started on {HOSTNAME}. Reporting to {SERVER_URL}...")
    
    while True:
        # 1. Run Checks
        fw_status, fw_msg = check_firewall()
        pw_status, pw_msg = check_password_policy()

        # 2. Prepare Payloads
        payloads = [
            {
                "hostname": HOSTNAME,
                "control_id": "A.13.1 (Network)",
                "status": fw_status,
                "details": fw_msg
            },
            {
                "hostname": HOSTNAME,
                "control_id": "A.9.4 (Access)",
                "status": pw_status,
                "details": pw_msg
            }
        ]

        # 3. Send to Server API
        for p in payloads:
            try:
                requests.post(SERVER_URL, json=p)
                print(f"[+] Sent report: {p['control_id']} -> {p['status']}")
            except:
                print("[-] Error: Could not connect to OpenGRC Server.")

        time.sleep(10) # Run every 10 seconds

if __name__ == "__main__":
    run_agent()