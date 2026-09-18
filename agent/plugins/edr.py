import psutil

EDR_PROCESSES = ["falcond", "sentinelctl", "MsMpEng.exe", "clamd"]

def check_edr_agent():
    try:
        running_procs = [p.name() for p in psutil.process_iter(['name'])]
        detected = [proc for proc in EDR_PROCESSES if any(proc.lower() in p.lower() for p in running_procs)]

        if detected:
            return "PASS", f"EDR agent(s) detected: {', '.join(detected)}"
        return "FAIL", "No recognized EDR / Antivirus process running."
    except Exception as e:
        return "WARNING", f"Could not audit EDR processes: {e}"
