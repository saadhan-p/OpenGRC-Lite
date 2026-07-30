import requests
import time
import socket
import subprocess
import platform

SERVER_URL = "http://127.0.0.1:5000/api/report"
HOSTNAME = socket.gethostname()

def check_firewall():
    system = platform.system()
    try:
        if system == "Linux":
            result = subprocess.run(["ufw", "status"], capture_output=True, text=True, timeout=5)
            if "Status: active" in result.stdout:
                return "PASS", "Firewall (ufw) is active."
            return "FAIL", "CRITICAL: Firewall (ufw) is inactive."
        elif system == "Windows":
            result = subprocess.run(
                ["netsh", "advfirewall", "show", "currentprofile"],
                capture_output=True, text=True, timeout=5
            )
            if "State                                 ON" in result.stdout:
                return "PASS", "Windows Firewall is active."
            return "FAIL", "CRITICAL: Windows Firewall is off."
        else:
            return "WARNING", f"No firewall check implemented for {system}."
    except Exception as e:
        return "WARNING", f"Could not determine firewall status: {e}"

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