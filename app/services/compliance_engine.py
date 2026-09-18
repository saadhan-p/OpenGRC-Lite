# Multi-Framework Compliance Scoring Engine

class ComplianceEngine:
    @staticmethod
    def calculate_score(total_checks: int, failed_checks: int) -> float:
        if total_checks == 0:
            return 100.0
        return round(((total_checks - failed_checks) / total_checks) * 100, 1)
