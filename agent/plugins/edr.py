import psutil
from agent.plugins.base import BasePlugin

EDR_PROCESSES = ["falcond", "sentinelctl", "MsMpEng.exe", "clamd"]

class EDRCheckPlugin(BasePlugin):
    check_id = "EDR_RUNNING"
    name = "EDR / Antivirus Protection Running"

    def run(self) -> dict:
        raw_evidence = {"running_edr_processes": []}
        try:
            running_procs = [p.name() for p in psutil.process_iter(['name'])]
            detected = [proc for proc in EDR_PROCESSES if any(proc.lower() in p.lower() for p in running_procs)]
            raw_evidence["running_edr_processes"] = detected

            if detected:
                status, details = "PASS", f"EDR agent(s) active: {', '.join(detected)}"
            else:
                status, details = "FAIL", "No recognized EDR / Antivirus process running."
        except Exception as e:
            status = "WARNING"
            details = f"Could not audit EDR processes: {e}"
            raw_evidence["error"] = str(e)

        return {
            "check_id": self.check_id,
            "status": status,
            "details": details,
            "raw_evidence": raw_evidence,
            "evidence_hash": self.compute_evidence_hash(raw_evidence)
        }
